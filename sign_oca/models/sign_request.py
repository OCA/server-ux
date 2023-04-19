# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SignRequest(models.Model):
    _name = "sign.request"
    _inherit = ["mail.thread"]
    _description = "Sign Request"
    _order = "date desc, name asc"

    name = fields.Char(
        string="Name",
        readonly=True,
        states={"draft": [("readonly", False)]},
        copy=False,
        default=lambda self: _("New"),
    )
    description = fields.Html(
        string="Description", readonly=True, states={"draft": [("readonly", False)]},
    )
    date = fields.Datetime(
        default=lambda self: fields.Datetime.now(),
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Responsible",
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=lambda self: self.env.user,
        required=True,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        readonly=True,
        states={"draft": [("readonly", False)]},
        required=True,
    )
    partner_user_id = fields.Many2one(
        comodel_name="res.users",
        compute="_compute_partner_user_id",
        store=True,
        string="Partner user",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.company,
        states={"draft": [("readonly", False)]},
    )
    state = fields.Selection(
        [("draft", "Draft"), ("in_progress", "Requested"), ("done", "Signed")],
        default="draft",
        copy=False,
        tracking=True,
    )
    record_ref = fields.Reference(
        lambda self: [(m.model, m.name) for m in self.env["ir.model"].search([])],
        string="Object",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    signature = fields.Image(
        string="Signature",
        copy=False,
        attachment=True,
        readonly=True,
        states={"in_progress": [("readonly", False)]},
        max_width=1024,
        max_height=1024,
    )
    signed_on = fields.Datetime(
        string="Signed On", help="Date of the signature.", readonly=True, copy=False
    )

    @api.depends("partner_id")
    def _compute_partner_user_id(self):
        for item in self:
            item.partner_user_id = fields.first(self.partner_id.user_ids)

    @api.onchange("record_ref")
    def _onchange_record_ref(self):
        if (
            not self.partner_id
            and self.record_ref
            and self.record_ref._name == "res.partner"
        ):
            self.partner_id = self.record_ref
        elif (
            not self.partner_id
            and self.record_ref
            and "partner_id" in self.record_ref._fields
        ):
            self.partner_id = self.record_ref.partner_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                ir_sequence = self.env["ir.sequence"]
                if "company_id" in vals:
                    ir_sequence = ir_sequence.with_context(
                        force_company=vals["company_id"]
                    )
                vals["name"] = ir_sequence.next_by_code("sign.request")
        return super().create(vals_list)

    def action_confirm(self):
        if any(request.state != "draft" for request in self):
            raise UserError(_("Requests is not in draft status"))
        for item in self:
            item.state = "in_progress"
            item.message_subscribe([item.partner_id.id])

    def _action_done(self):
        for item in self.sudo():
            item.write({"state": "done", "signed_on": fields.Datetime.now()})

    def action_done(self):
        if any(request.state != "in_progress" for request in self):
            raise UserError(_("Request is not in progress status"))
        if any(not request.signature for request in self):
            raise UserError(_("Signature is required"))
        self._action_done()
