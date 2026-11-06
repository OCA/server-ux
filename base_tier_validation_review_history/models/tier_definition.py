# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class TierDefinition(models.Model):
    _inherit = "tier.definition"

    keep_review_history = fields.Selection(
        selection=[
            ("keep", "Keep"),
            ("no_keep", "Do Not Keep"),
        ],
        string="Keep Tier Review History",
        help="Override the company default for keeping completed reviews as "
        "history. Leave empty to inherit the company setting.",
    )

    def _keep_review_history_enabled(self):
        """Resolve whether completed reviews of this definition are kept as
        history. The definition overrides the company default in either
        direction; an empty value inherits the company setting."""
        self.ensure_one()
        if self.keep_review_history == "keep":
            return True
        if self.keep_review_history == "no_keep":
            return False
        # A definition without company applies to every company, so it falls back
        # to the setting of the company the validation is running for.
        company = self.company_id or self.env.company
        return company.tier_validation_keep_review_history
