# Copyright 2020 Ecosoft Co., Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import datetime
import logging
import time
from collections import defaultdict

import dateutil

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.modules.module import get_module_resource
from odoo.tools.safe_eval import safe_eval

CRITICAL_FIELDS = ["reference_model", "force_approval"]
APPROVAL_STATUS = [
    ("new", "New"),
    ("pending", "Pending Approval"),
    ("approved", "Approved"),
    ("refused", "Refused"),
    ("cancel", "Cancel"),
]

_logger = logging.getLogger(__name__)


class TierApprovalCategory(models.Model):
    _name = "tier.approval.category"
    _description = "Tier Approval Category"
    _order = "sequence"

    def _get_default_image(self):
        default_image_path = get_module_resource(
            "approvals_tier_validation", "static/src/img", "clipboard-check-solid.svg"
        )
        return base64.b64encode(open(default_image_path, "rb").read())

    name = fields.Char(string="Name", translate=True, required=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(string="Sequence")
    description = fields.Char(string="Description", translate=True)
    image = fields.Binary(string="Image", default=_get_default_image)
    require_document = fields.Selection(
        [("required", "Required"), ("optional", "Optional")],
        string="Documents",
        default="optional",
        required=True,
    )
    request_to_validate_count = fields.Integer(
        "Number of requests to validate", compute="_compute_request_to_validate_count"
    )
    reference_model = fields.Selection(
        string="Reference Model", selection="_selection_target_model", required=True,
    )
    approval_model_id = fields.Many2one(
        string="Model",
        comodel_name="ir.model",
        default=lambda s: s.env["ir.model"]._get("tier.approval.request").id,
        required=True,
    )
    rec_action_id = fields.Many2one(
        string="Window Action",
        comodel_name="ir.actions.act_window",
        domain="[('res_model', '=', reference_model)]",
        required=True,
    )
    rec_view_id = fields.Many2one(
        string="Form View",
        comodel_name="ir.ui.view",
        domain="[('model', '=', reference_model),"
        "('type', '=', 'form'), ('mode', '=', 'primary')]",
        required=True,
    )
    # Any document that satisfy following updates will need this approval type
    force_approval = fields.Boolean(
        string="Enforce Approval",
        help="If checked, documents of selected model required in approval process",
    )
    filter_pre_domain = fields.Char(
        string="Before Update Domain",
        help="If present, this condition must be satisfied "
        "before the update of the record.",
    )
    filter_domain = fields.Char(
        string="Apply on",
        help="If present, this condition must be satisfied "
        "before executing the action rule.",
    )
    # Lock document if the approval process is in progress
    lock_doc_wip = fields.Boolean(
        string="Lock Document In-Progress",
        default=True,
        index=True,
        help="Lock document if any approval is in progress",
    )
    add_doc_action = fields.Boolean(
        string="Add Approval Actions",
        help="Add start approval action, and approval status to target document",
    )
    # Tier definition
    tier_definition_ids = fields.One2many(
        string="Tier Definitions",
        comodel_name="tier.definition",
        inverse_name="approval_category_id",
    )
    # Advance Control
    doc_begin_domain = fields.Char(
        string="Ref document begin condition",
        help="Required document condition when approval request starts",
    )
    new_expr = fields.Text(
        default=lambda self: self._default_expr(),
        help="Executed after state changed to 'new'",
    )
    pending_expr = fields.Text(
        default=lambda self: self._default_expr(),
        help="Executed after state changed to 'pending'",
    )
    approved_expr = fields.Text(
        default=lambda self: self._default_expr(),
        help="Executed after state changed to 'approved'",
    )
    refused_expr = fields.Text(
        default=lambda self: self._default_expr(),
        help="Executed after state changed to 'refused'",
    )
    cancel_expr = fields.Text(
        default=lambda self: self._default_expr(),
        help="Executed after state changed to 'cancel'",
    )

    @api.model
    def _default_expr(self):
        return (
            "# Available locals:\n#  - rec: current record\n"
            "#  - doc: reference document\nTrue"
        )

    @api.model
    def _selection_target_model(self):
        models = self.env["ir.model"].search([])
        return [(model.model, model.name) for model in models]

    def _compute_request_to_validate_count(self):
        domain = [("state", "=", "pending"), ("reviewer_ids", "=", self.env.user.id)]
        requests_data = self.env["tier.approval.request"].read_group(
            domain, ["category_id"], ["category_id"]
        )
        requests_mapped_data = {
            data["category_id"][0]: data["category_id_count"] for data in requests_data
        }
        for category in self:
            category.request_to_validate_count = requests_mapped_data.get(
                category.id, 0
            )

    def create_request(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "tier.approval.request",
            "views": [[False, "form"]],
            "context": {
                "form_view_initial_mode": "edit",
                "default_name": self.name,
                "default_category_id": self.id,
                "default_request_owner_id": self.env.user.id,
                "default_state": "new",
            },
        }

    def _get_categories(self, records):
        domain = [("reference_model", "=", records._name)]
        categories = self.search(domain)
        return categories

    def _get_eval_context(self):
        """ Prepare the context used when evaluating python code
            :returns: dict -- evaluation context given to safe_eval
        """
        return {
            "datetime": datetime,
            "dateutil": dateutil,
            "time": time,
            "uid": self.env.uid,
            "user": self.env.user,
        }

    def _filter_pre(self, records):
        """ Filter the records that satisfy the precondition of action ``self``. """
        if self.filter_pre_domain and records:
            domain = [("id", "in", records.ids)] + safe_eval(
                self.filter_pre_domain, self._get_eval_context()
            )
            return records.sudo().search(domain)
        else:
            return records

    def _filter_post(self, records):
        """ Filter the records that satisfy the postcondition of action ``self``. """
        if self.filter_domain and records:
            domain = [("id", "in", records.ids)] + safe_eval(
                self.filter_domain, self._get_eval_context()
            )
            return records.sudo().search(domain)
        else:
            return records

    def _create_approval_status_view(self):
        for rec in self:
            appr_view = self.env["ir.ui.view"].search(
                [
                    ("name", "=", "%s.tier.approval" % rec.rec_view_id.name),
                    ("type", "=", "form"),
                    ("model", "=", rec.reference_model),
                ]
            )
            if not appr_view:
                action_id = (
                    self.env["ir.actions.server"]
                    .search(
                        [
                            ("model_id.model", "=", rec.reference_model),
                            ("state", "=", "code"),
                            (
                                "code",
                                "like",
                                "tier_approval_from_document(%s)" % rec.id,
                            ),
                        ]
                    )
                    .id
                )
                appr_view = self.env["ir.ui.view"].create(
                    {
                        "name": "%s.tier.approval" % rec.rec_view_id.name,
                        "type": "form",
                        "model": rec.reference_model,
                        "mode": "extension",
                        "inherit_id": rec.rec_view_id.id,
                        "arch_base": """<?xml version="1.0"?>
<data><header position="after">
<field name="x_tier_approval_status" invisible="1"/>
<div class="alert-success" role="alert" style="margin-bottom:0px;" align="right"
    attrs="{'invisible': [('x_tier_approval_status', '!=', 'approved')]}">
<button name="%s" string="Approved" type="action" class="oe_link"/>
</div>
<div class="alert-warning" role="alert" style="margin-bottom:0px;" align="right"
    attrs="{'invisible': [('x_tier_approval_status', '!=', 'pending')]}">
<button name="%s" string="Approval In-Progress" type="action" class="oe_link"/>
</div>
<div class="alert-danger" role="alert" style="margin-bottom:0px;" align="right"
    attrs="{'invisible': [('x_tier_approval_status', '!=', 'rejected')]}">
<button name="%s" string="Approval Rejected" type="action" class="oe_link"/>
</div>
</header></data>
                    """
                        % (action_id, action_id, action_id),
                    }
                )

    def _remove_approval_status_view(self):
        for rec in self:
            appr_view = self.env["ir.ui.view"].search(
                [
                    ("name", "=", "%s.tier.approval" % rec.rec_view_id.name),
                    ("type", "=", "form"),
                    ("model", "=", rec.reference_model),
                ]
            )
            appr_view.unlink()

    def _create_approval_status_field(self):
        for rec in self:
            appr_field = self.env["ir.model.fields"].search(
                [
                    ("model", "=", rec.reference_model),
                    ("name", "=", "x_tier_approval_status"),
                ]
            )
            if not appr_field:
                _model = self.env["ir.model"].search(
                    [("model", "=", rec.reference_model)]
                )
                status_list = [
                    (0, 0, {"value": x[0], "name": x[1]}) for x in APPROVAL_STATUS
                ]
                vals = {
                    "name": "x_tier_approval_status",
                    "field_description": "Approval status",
                    "ttype": "selection",
                    "selection_ids": status_list,
                    "store": False,
                    "depends": "display_name",
                    "compute": "for rec in self:\n"
                    "    appr = self.env['tier.approval.request'].search("
                    "[('reference_model', '=', rec._name), "
                    "('reference_rec_id', '=', rec.id)], limit=1)\n"
                    "    rec['x_tier_approval_status'] = appr.state",
                }
                _model.write({"field_id": [(0, 0, vals)]})

    def _remove_approval_status_field(self):
        appr_fields = self.env["ir.model.fields"].search(
            [
                ("model", "in", self.mapped("reference_model")),
                ("name", "=", "x_tier_approval_status"),
            ]
        )
        appr_fields.unlink()

    def _create_tier_approval_action(self, activate=True):
        for rec in self:
            appr_action = self.env["ir.actions.server"].search(
                [
                    ("model_id.model", "=", rec.reference_model),
                    ("state", "=", "code"),
                    ("code", "like", "tier_approval_from_document(%s)" % rec.id),
                ]
            )
            if not appr_action:
                appr_action = self.env["ir.actions.server"].create(
                    {
                        "name": "Tier Approval Workflow",
                        "model_id": self.env["ir.model"]._get(rec.reference_model).id,
                        "state": "code",
                        "code": (
                            "action = env['tier.approval.request']."
                            "tier_approval_from_document(%s)"
                        )
                        % rec.id,
                    }
                )
            appr_action.create_action()

    def _remove_tier_approval_action(self):
        for rec in self:
            appr_action = self.env["ir.actions.server"].search(
                [
                    ("model_id.model", "=", rec.reference_model),
                    ("state", "=", "code"),
                    ("code", "like", "tier_approval_from_document(%s)" % rec.id),
                ]
            )
            appr_action.unlink()

    @api.model
    def create(self, vals):
        res = super().create(vals)
        self._update_registry()
        # Create approval status in target document model
        if "add_doc_action" in vals:
            if vals["add_doc_action"]:
                res._create_approval_status_field()
                res._create_tier_approval_action()
                res._create_approval_status_view()
            else:
                res._remove_approval_status_view()
                res._remove_approval_status_field()
                res._remove_tier_approval_action()
        return res

    def write(self, vals):
        res = super().write(vals)
        if set(vals).intersection(CRITICAL_FIELDS):
            self._update_registry()
        # Create approval status in target document model
        if "add_doc_action" in vals:
            if vals["add_doc_action"]:
                self._create_approval_status_field()
                self._create_tier_approval_action()
                self._create_approval_status_view()
            else:
                self._remove_approval_status_view()
                self._remove_approval_status_field()
                self._remove_tier_approval_action()
        return res

    def unlink(self):
        self._remove_approval_status_view()
        self._create_approval_status_field()
        self._create_tier_approval_action()
        res = super().unlink()
        self._update_registry()
        return res

    def get_field_name(self, code=False):
        return "x__{}".format(code or self.code)

    def _update_registry(self):
        """ Update the registry after a modification on approval type. """
        if self.env.registry.ready:
            # re-install the model patches, and notify other workers
            self._unregister_hook()
            self._register_hook()
            self.env.registry.registry_invalidated = True

    # flake8: noqa: C901
    def _register_hook(self):
        """ Patch models that should check its approval workflow condition """

        def make_create():
            """ Instanciate a create method that processes action rules. """

            @api.model
            def create(self, vals):
                # call original method
                record = create.origin(self, vals)
                # link newly created record with its related approval
                link_appr = self._context.get("link_appr", False)
                active_model = self._context.get("active_model", False)
                active_id = self._context.get("active_id", False)
                if link_appr and active_model == "tier.approval.request":
                    request = self.env[active_model].browse(active_id)
                    if request.reference_rec_id or request.reference_rec:
                        raise UserError(
                            _("%s already has Ref. Document") % request.display_name
                        )
                    request.write(
                        {
                            "reference_rec_id": record.id,
                            "reference_rec": "{},{}".format(self._name, record.id),
                        }
                    )
                return record

            return create

        def make_copy():
            def copy(self, default=None):
                self = self.with_context(link_appr=False)
                return copy.origin(self, default=default)

            return copy

        def make_write():
            """ Instanciate a write method that processes action rules. """

            def write(self, vals):
                records = self
                # retrieve the action rules to possibly execute
                categories = self.env["tier.approval.category"]._get_categories(records)
                # check preconditions on records
                pre = {
                    categ: categ._filter_pre(records)
                    for categ in categories.filtered("force_approval")
                }
                # call original method
                write.origin(records, vals)
                # 1. check lock_doc_wip
                domain = [
                    ("reference_rec_id", "in", self._ids),
                    ("reference_model", "=", self._name),
                    ("category_id.lock_doc_wip", "=", True),
                    ("category_id", "in", categories._ids),
                    ("state", "=", "pending"),
                ]
                active_requests = self.env["tier.approval.request"].search(domain)
                if active_requests:
                    raise UserError(
                        _(
                            "This document is under approval process, "
                            "modification is not allowed!\nApproval Ref: %s"
                        )
                        % ", ".join(active_requests.mapped("name"))
                    )
                # 2. check force_approval for document satisfy filter option
                for categ in categories.filtered("force_approval"):
                    documents = categ._filter_post(pre[categ])
                    for doc in documents:  # These document must be approved
                        domain = [
                            ("reference_rec_id", "=", doc.id),
                            ("reference_model", "=", doc._name),
                            ("category_id", "=", categ.id),
                            ("state", "=", "approved"),
                        ]
                        request = self.env["tier.approval.request"].search(domain)
                        if not request:
                            raise UserError(
                                _(
                                    "This document require approval (%s).\n"
                                    "If a workflow is not started, you can "
                                    "start it from actions menu."
                                )
                                % categ.display_name
                            )
                return True

            return write

        patched_models = defaultdict(set)

        def patch(model, name, method):
            """ Patch method `name` on `model`, unless it has been patched already. """
            if model not in patched_models[name]:
                patched_models[name].add(model)
                model._patch_method(name, method)

        # retrieve all categories, and patch their corresponding model
        for categ in self.search([]):
            Model = self.env.get(categ.reference_model)
            # Do not crash if the model of the approval category was uninstalled
            if Model is None:
                _logger.warning(
                    "Approval Category with ID %d depends on model %s"
                    % (categ.id, categ.reference_model)
                )
                continue
            patch(Model, "create", make_create())
            patch(Model, "copy", make_copy())
            patch(Model, "write", make_write())

    def _unregister_hook(self):
        """ Remove the patches installed by _register_hook() """
        NAMES = ["create", "write"]
        for Model in self.env.registry.values():
            for name in NAMES:
                try:
                    delattr(Model, name)
                except AttributeError:
                    pass
