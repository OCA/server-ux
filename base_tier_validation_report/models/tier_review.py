# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TierReview(models.Model):
    _inherit = "tier.review"

    resource_ref = fields.Reference(
        selection="_selection_resource_ref",
        compute="_compute_resource_ref",
        store=True,
        readonly=True,
        compute_sudo=True,
    )
    resource_type = fields.Selection(
        selection="_selection_resource_ref",
        compute="_compute_display_fields",
        compute_sudo=True,
    )
    resource_name = fields.Char(
        compute="_compute_display_fields",
        compute_sudo=True,
    )
    next_review = fields.Char(
        compute="_compute_display_fields",
        compute_sudo=True,
    )

    def _selection_resource_ref(self):
        models = self.env["tier.definition"]._get_tier_validation_model_names()
        res = [(m, self.env[m]._description) for m in models]
        return res

    @api.depends("model", "res_id")
    def _compute_resource_ref(self):
        for rec in self:
            rec.resource_ref = f"{rec.model},{rec.res_id}" if rec.res_id else False

    @api.depends("model", "res_id", "resource_ref")
    def _compute_display_fields(self):
        for rec in self:
            rec.resource_type = rec.model
            rec.resource_name = rec.resource_ref.display_name
            rec.next_review = rec.next_review

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
