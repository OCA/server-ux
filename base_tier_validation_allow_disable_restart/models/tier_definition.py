# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class TierValidation(models.Model):
    _inherit = "tier.definition"

    disable_validation_restart = fields.Boolean(
        help="If checked, the validation restart feature will be disabled.",
        default=False,
    )
