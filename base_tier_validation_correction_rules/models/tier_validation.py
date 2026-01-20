# Copyright 2026 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TierValidation(models.AbstractModel):
    _inherit = "tier.validation"

    is_group_definition = fields.Boolean(
        compute="_compute_is_group_definition",
    )

    def view_tier_correction(self):
        """Override to open the tier correction wizard instead of standard form."""
        self.ensure_one()
        return {
            "name": self.env._("Change Reviewers"),
            "type": "ir.actions.act_window",
            "res_model": "tier.correction.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "active_model": self._name,
                "active_id": self.id,
            },
        }

    @api.depends("review_ids.definition_id", "review_ids.status")
    def _compute_is_group_definition(self):
        for record in self:
            record.is_group_definition = any(
                review.status in ("waiting", "pending")
                and review.definition_id
                and review.definition_id.review_type == "group"
                for review in record.review_ids
            )
