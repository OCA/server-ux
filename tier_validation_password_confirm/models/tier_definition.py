# Copyright 2024 ForgeFlow S.L.

from odoo import fields, models


class TierDefinition(models.Model):
    _inherit = "tier.definition"

    require_password = fields.Boolean(
        help="If checked, the user will be asked to enter "
        "the password to validate the tier.",
    )
