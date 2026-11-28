# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TierReview(models.Model):
    _inherit = "tier.review"

    active = fields.Boolean(default=True)
    record_reference = fields.Reference(
        string="Document",
        selection="_selection_record_reference",
        compute="_compute_record_reference",
        help="The document under validation, as a clickable link.",
    )
    res_name = fields.Char(
        string="Document Name",
        compute="_compute_res_name",
        store=True,
        help="Document display name, stored so the list can be grouped and sorted "
        "by document. Captured from the record and not refreshed if the record is "
        "later renamed.",
    )

    @api.model
    def _selection_record_reference(self):
        model_names = self.env["tier.definition"]._get_tier_validation_model_names()
        ir_models = self.env["ir.model"].sudo().search([("model", "in", model_names)])
        return [(m.model, m.name) for m in ir_models]

    @api.depends("model", "res_id")
    def _compute_record_reference(self):
        for record in self:
            if record.model and record.res_id and record.model in self.env:
                record.record_reference = "{},{}".format(record.model, record.res_id)
            else:
                record.record_reference = None

    @api.depends("model", "res_id")
    def _compute_res_name(self):
        for record in self:
            name = False
            if record.model and record.res_id and record.model in self.env:
                target = self.env[record.model].browse(record.res_id).exists()
                name = target.display_name if target else False
            record.res_name = name
