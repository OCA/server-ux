# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class WizardSignRequest(models.TransientModel):
    _name = "wizard.sign.request"
    _description = "Wizard Sign Request"

    auto_confirm = fields.Boolean(string="Auto confirm?", default=True)
    res_model = fields.Char(readonly=True)
    line_ids = fields.One2many(
        comodel_name="wizard.sign.request.line",
        inverse_name="wizard_id",
        string="Lines",
    )

    def _prepare_line_vals(self, record):
        res = {
            "record_ref": "%s,%s" % (record._name, record.id),
        }
        if record._name == "res.partner":
            res.update({"partner_id": record.id})
        elif record._name != "res.partner" and "partner_id" in record._fields:
            res.update({"partner_id": record.partner_id.id})
        return res

    def _prepare_lines_vals(self):
        lines = []
        active_ids = self.env.context.get("active_ids", [])
        for item in self.env[self.env.context.get("active_model")].browse(active_ids):
            vals = self._prepare_line_vals(item)
            lines.append((0, 0, vals))
        return lines

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        res.update(
            {
                "res_model": self.env.context.get("active_model"),
                "line_ids": self._prepare_lines_vals(),
            }
        )
        return res

    def _prepare_sign_requests_vals(self):
        values = []
        for line in self.line_ids:
            values.append(line._prepare_sign_request_vals())
        return values

    def action_process(self):
        if not self.res_model:
            raise UserError(_("Model is required"))
        if not self.line_ids:
            raise UserError(_("Any line is required"))
        if any(not line.partner_id for line in self.line_ids):
            raise UserError(_("Partner is required for all lines"))
        # create requests
        requests = (
            self.env["sign.request"].sudo().create(self._prepare_sign_requests_vals())
        )
        if self.auto_confirm:
            requests.action_confirm()
        # return request list
        action = self.env.ref("sign_oca.sign_request_all_action")
        result = action.read()[0]
        result["domain"] = [("id", "in", requests.ids)]
        return result


class WizardSignRequestLine(models.TransientModel):
    _name = "wizard.sign.request.line"
    _description = "Wizard Sign Request Line"

    wizard_id = fields.Many2one(comodel_name="wizard.sign.request",)
    record_ref = fields.Reference(
        lambda self: [(m.model, m.name) for m in self.env["ir.model"].search([])],
        string="Object",
        readonly=True,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner", string="Partner", required=True
    )

    def _prepare_sign_request_vals(self):
        return {
            "record_ref": "%s,%s" % (self.record_ref._name, self.record_ref.id),
            "partner_id": self.partner_id.id,
        }
