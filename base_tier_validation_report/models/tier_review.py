# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TierReview(models.Model):
    _inherit = "tier.review"

    resource_ref = fields.Reference(
        string="Resource Ref",
        selection="_selection_resource_ref",
        compute="_compute_resource_ref",
        store=True,
        readonly=True,
    )

    def _selection_resource_ref(self):
        models = self.env["tier.definition"]._get_tier_validation_model_names()
        return [(m, m) for m in models]

    @api.depends("model", "res_id")
    def _compute_resource_ref(self):
        for rec in self:
            rec.resource_ref = (
                "%s,%s" % (rec.model, rec.res_id) if rec.res_id else False
            )

    def action_open_resource_ref(self):
        self.ensure_one()
        return {
            "name": self.resource_ref.display_name,
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": self.model,
            "res_id": self.res_id,
        }
