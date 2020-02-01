# Copyright 2020 Ecosoft Co., Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from ast import literal_eval
import datetime
import time
import dateutil

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

from .tier_approval_category import APPROVAL_STATUS


class TierApprovalRequest(models.Model):
    _name = "tier.approval.request"
    _description = "Approval Request"
    _inherit = ["tier.validation", "mail.thread", "mail.activity.mixin"]
    _state_from = ["pending"]
    _state_to = ["approved"]
    _cancel_state = "refused"

    @api.model
    def _read_group_state(self, stages, domain, order):
        request_status_list = dict(self._fields["state"].selection).keys()
        return request_status_list

    name = fields.Char(string="Approval Subject", tracking=True)
    category_id = fields.Many2one(
        "tier.approval.category",
        string="Category",
        index=True,
        required=True,
        readonly=True,
    )
    request_owner_id = fields.Many2one("res.users", string="Request Owner")
    attachment_number = fields.Integer(
        "Number of Attachments", compute="_compute_attachment_number"
    )
    date_confirmed = fields.Datetime(string="Date Confirmed")
    require_document = fields.Selection(related="category_id.require_document")
    reason = fields.Text(string="Description")
    state = fields.Selection(
        APPROVAL_STATUS, default="new", tracking=True, group_expand="_read_group_state",
    )
    reference_model = fields.Selection(
        string="Document Type",
        selection="_selection_target_model",
        related="category_id.reference_model",
        store=True,
        readonly=True,
    )
    reference_rec = fields.Reference(
        string="Reference Record", selection="_selection_target_model", copy=False,
    )
    reference_rec_id = fields.Integer(
        string="Reference Record ID", index=True, copy=False,
    )
    reference_rec_name = fields.Char(compute="_compute_reference_rec_name",)
    rec_action_id = fields.Many2one(
        comodel_name="ir.actions.act_window", related="category_id.rec_action_id"
    )
    rec_view_id = fields.Many2one(
        comodel_name="ir.ui.view", related="category_id.rec_view_id"
    )

    def validate_tier(self):
        super().validate_tier()
        if self.validated:
            self.action_approve()

    def reject_tier(self):
        super().reject_tier()
        if self.rejected:
            self.action_refuse()

    @api.constrains("reference_rec", "state")
    def _check_reference_rec(self):
        for request in self:
            if not request.reference_model and request.reference_rec:
                raise UserError(_("Reference record should be nothing"))
            if request.reference_model and request.state == "pending":
                if not request.reference_rec:
                    raise UserError(_("Please click 'Create Ref. Document'"))
                if request.reference_rec._name != request.reference_model:
                    raise UserError(_("Reference Record is of the wrong type"))

    @api.model
    def _selection_target_model(self):
        models = self.env["ir.model"].search([])
        return [(model.model, model.name) for model in models]

    def _compute_attachment_number(self):
        domain = [
            ("res_model", "=", "tier.approval.request"),
            ("res_id", "in", self.ids),
        ]
        attachment_data = self.env["ir.attachment"].read_group(
            domain, ["res_id"], ["res_id"]
        )
        attachment = {data["res_id"]: data["res_id_count"] for data in attachment_data}
        for request in self:
            request.attachment_number = attachment.get(request.id, 0)

    def _compute_reference_rec_name(self):
        for request in self:
            request.reference_rec_name = (
                request.reference_rec and request.reference_rec.display_name or False
            )

    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env["ir.actions.act_window"].for_xml_id("base", "action_attachment")
        res["domain"] = [
            ("res_model", "=", "tier.approval.request"),
            ("res_id", "in", self.ids),
        ]
        res["context"] = {
            "default_res_model": "tier.approval.request",
            "default_res_id": self.id,
        }
        return res

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

    def _check_doc_begin_domain(self):
        """ With begin doc condition, test if reference document condition is met"""
        doc_condition = self.category_id.doc_begin_domain
        if doc_condition and self.reference_rec:
            domain = [("id", "=", self.reference_rec.id)] + \
                     safe_eval(doc_condition, self._get_eval_context())
            if not self.env[self.reference_model].sudo().search(domain):
                raise UserError(
                    _("Document %s must be in valid beginning condition in order "
                      "to start.\nRef condition: %s") %
                    (self.reference_rec.display_name, doc_condition)
                )

    def action_confirm(self):
        self.ensure_one()
        if self.require_document == "required" and not self.attachment_number:
            raise UserError(_("You have to attach at least one document."))
        # Test reference document exists
        if not self.reference_rec:
            raise UserError(_("Please create Ref. Record to approve."))
        # When start approval, check document condition is met
        self._check_doc_begin_domain()
        self.write({"state": "pending", "date_confirmed": fields.Datetime.now()})
        self.request_validation()

    def action_approve(self, approver=None):
        self.write({"state": "approved"})

    def action_refuse(self, approver=None):
        self.write({"state": "refused"})

    def action_draft(self):
        if self.env.user.has_group("approvals_tier_validation.group_approval_manager"):
            self.write({"state": "new"})
            self.restart_validation()
        else:
            raise UserError(_("Only approval manager can take this action"))

    def action_cancel(self):
        if self.env.user.has_group("approvals_tier_validation.group_approval_manager"):
            self.write({"state": "cancel"})
        else:
            raise UserError(_("Only approval manager can take this action"))

    def evaluate_state_expr(self, expr):
        self.ensure_one()
        try:
            res = safe_eval(expr, globals_dict={"rec": self, "doc": self.reference_rec})
        except Exception as error:
            raise UserError(_("Error evaluating state expression.\n %s") % error)
        return res

    def write(self, vals):
        res = super().write(vals)
        if "state" in vals:
            for rec in self:
                expr = rec.category_id["%s_expr" % vals["state"]]
                rec.evaluate_state_expr(expr)
        return res

    def open_reference_rec(self):
        self.ensure_one()
        if self.reference_rec:
            result = self.create_reference_rec()
            result["res_id"] = self.reference_rec.id
            return result
        else:
            raise UserError(_("No reference record found"))

    def create_reference_rec(self):
        self.ensure_one()
        ctx = {"link_appr": True}
        # Default action
        result = {
            "type": "ir.actions.act_window",
            "name": _("Create Ref. Document"),
            "res_model": self.reference_model,
            "view_mode": "form",
            "context": ctx,
        }
        if self.rec_action_id:
            action = self.env.ref(self.rec_action_id.xml_id)
            result = action.read()[0]
            action_context = literal_eval(result["context"])
            result["view_mode"] = "form"
            result["context"] = {**action_context, **ctx}
        if self.rec_view_id:
            view = (self.rec_view_id.id, self.rec_view_id.name)
            result["view_id"] = view
            result["views"] = []
        return result

    @api.model
    def tier_approval_from_document(self, category_id):
        """ Given a document reference, this function create a new approval """
        res_model = self._context["active_model"]
        res_id = self._context["active_id"]
        document = self.env[res_model].browse(res_id)
        # Check if the approval request already exists
        request = self.search(
            [
                ("category_id", "=", category_id),
                ("reference_model", "=", res_model),
                ("reference_rec_id", "=", res_id),
            ],
            limit=1,
        )
        if not request:
            return {
                "type": "ir.actions.act_window",
                "res_model": "tier.approval.request",
                "views": [[False, "form"]],
                "context": {
                    "form_view_initial_mode": "edit",
                    "default_name": document.display_name,
                    "default_category_id": category_id,
                    "default_request_owner_id": self.env.user.id,
                    "default_reference_rec_id": res_id,
                    "default_reference_rec": "{},{}".format(res_model, res_id),
                },
            }
        # Open the request
        action = self.env.ref(
            "approvals_tier_validation.tier_approval_request_action_all"
        )
        result = action.read()[0]
        result["view_mode"] = "form"
        result["views"] = []
        result["res_id"] = request.id
        return result
