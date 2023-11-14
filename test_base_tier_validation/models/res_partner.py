# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "tier.validation"]
    _state_field = "test_state_tier_validation"
    _state_from = ["draft", "sent"]
    _state_to = ["done"]
    _tier_validation_manual_config = False

    test_state_tier_validation = fields.Selection(
        selection=[("draft", "Draft"), ("sent", "In progress"), ("done", "Done")],
        default="draft",
        string="State tier validation",
    )
