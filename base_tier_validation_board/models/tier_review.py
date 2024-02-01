# Copyright 2024 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class TierReview(models.Model):
    _inherit = "tier.review"

    @api.depends("model", "res_id")
    def _compute_res_name(self):
        for record in self:
            if record.res_id and record.model:
                record.res_name = (
                    self.env[record.model].browse(record.res_id).display_name
                )
            else:
                record.res_name = False

    related_model_instance = fields.Reference(
        selection="_selection_related_model_instance",
        compute="_compute_related_model_instance",
        string="Document",
    )
    res_name = fields.Char(
        "Resource Name", compute="_compute_res_name", compute_sudo=True
    )

    @api.depends("res_id", "model")
    def _compute_related_model_instance(self):
        for record in self:
            ref = False
            if record.res_id:
                ref = "{},{}".format(record.model, record.res_id)
            record.related_model_instance = ref

    @api.model
    def _selection_related_model_instance(self):
        models = self.env["tier.definition"].sudo().search([]).mapped("model_id")
        return [(model.model, model.name) for model in models]

    def open_origin(self):
        self.ensure_one()
        vid = self.env[self.model].browse(self.res_id).get_formview_id()
        response = {
            "type": "ir.actions.act_window",
            "res_model": self.model,
            "view_mode": "form",
            "res_id": self.res_id,
            "target": "current",
            "views": [(vid, "form")],
        }
        return response
