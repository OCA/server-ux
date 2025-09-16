# Copyright 2024 ForgeFlow S.L.
from odoo import fields, models


class TierReview(models.Model):
    _inherit = "tier.review"

    require_password = fields.Boolean(
        related="definition_id.require_password", readonly=True
    )
    password_confirmed = fields.Boolean()
