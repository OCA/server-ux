from odoo import fields, models


class TierValidationException(models.Model):
    _inherit = "tier.validation.exception"

    is_blacklist = fields.Boolean(
        string="Is Blacklist Exception",
        help="If checked, the selected fields will be skiped "
        "in allowed fields for tier validation.",
    )
