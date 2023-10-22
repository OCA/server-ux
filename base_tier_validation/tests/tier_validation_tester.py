# Copyright 2018-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TierValidationTester(models.Model):
    _name = "tier.validation.tester"
    _description = "Tier Validation Tester"
    _inherit = ["tier.validation", "mail.thread"]
    _tier_validation_manual_config = True

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("cancel", "Cancel"),
        ],
        default="draft",
    )
    test_field = fields.Float()
    user_id = fields.Many2one(string="Assigned to:", comodel_name="res.users")

    def action_confirm(self):
        self.write({"state": "confirmed"})


class TierValidationTester2(models.Model):
    _name = "tier.validation.tester2"
    _description = "Tier Validation Tester 2"
    _inherit = ["tier.validation"]
    _tier_validation_manual_config = False

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("cancel", "Cancel"),
        ],
        default="draft",
    )
    test_field = fields.Float()
    user_id = fields.Many2one(string="Assigned to:", comodel_name="res.users")

    def action_confirm(self):
        self.write({"state": "confirmed"})


class TierDefinition(models.Model):
    _inherit = "tier.definition"

    @api.model
    def _get_tier_validation_model_names(self):
        res = super()._get_tier_validation_model_names()
        res.append("tier.validation.tester")
        res.append("tier.validation.tester2")
        return res
