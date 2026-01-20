# Copyright 2026 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class TierValidation(models.AbstractModel):
    _inherit = "tier.validation"

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
