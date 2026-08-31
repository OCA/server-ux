# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class TierValidation(models.AbstractModel):
    _inherit = "tier.validation"

    disable_validation_restart = fields.Boolean(
        help="If checked, disable the restart feature.",
        compute="_compute_disable_validation_restart",
    )

    @api.depends("review_ids.definition_id.disable_validation_restart")
    def _compute_disable_validation_restart(self):
        """Compute the disable_validation_restart field."""
        for record in self:
            record.disable_validation_restart = record.review_ids.filtered(
                lambda r: r.definition_id.disable_validation_restart
                and r.status == "pending"
            ).exists()

    def restart_validation(self):
        """Disable restart validation feature."""
        if self.disable_validation_restart:
            raise UserError(_("Restart validation is disabled for review definition"))

        return super().restart_validation()
