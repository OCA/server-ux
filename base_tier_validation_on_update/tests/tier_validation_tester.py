# Copyright 2018-19 ForgeFlow S.L. (https://www.forgeflow.com)
# Copyright (C) 2024 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TierValidationTesterUpdate(models.Model):
    _name = "tier.validation.tester.update"
    _description = "Tier Validation Tester On Update"
    _inherit = ["tier.validation", "mail.thread"]
    _tier_validation_manual_config = True
    # Same as in base_tier_validation but with more fields

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("progress", "In progress"),
            ("confirmed", "Confirmed"),
            ("cancel", "Cancel"),
        ],
        default="draft",
    )
    test_field = fields.Float()
    user_id = fields.Many2one(comodel_name="res.users")
    tester2_ids = fields.One2many(
        comodel_name="tier.validation.tester2.update",
        inverse_name="tester1_id",
    )

    def action_confirm(self):
        self.write({"state": "confirmed"})


class TierValidationTester2Update(models.Model):
    _name = "tier.validation.tester2.update"
    _description = "Tier Validation Tester 2 On Update"
    _inherit = ["tier.validation"]
    _tier_validation_manual_config = False
    # Same as in base_tier_validation but with more fields

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("cancel", "Cancel"),
        ],
        default="draft",
    )
    test_field = fields.Float()
    user_id = fields.Many2one(comodel_name="res.users")

    tester1_id = fields.Many2one(
        comodel_name="tier.validation.tester.update",
    )
    name = fields.Char()

    def action_confirm(self):
        self.write({"state": "confirmed"})


class TierDefinition(models.Model):
    _inherit = "tier.definition"

    @api.model
    def _get_tier_validation_model_names(self):
        res = super()._get_tier_validation_model_names()
        res.append(["tier.validation.tester.update", "tier.validation.tester2.update"])
        return res
