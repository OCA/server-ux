# Copyright 2020 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class BaseSubstateType(models.Model):
    _name = "base.substate.type"
    _inherit = "base.substate.type"

    model = fields.Selection(selection_add=[("tier.validation.tester", "Tier Tester")])


class TierValidationTester(models.Model):
    _name = "tier.validation.tester"
    _inherit = ["tier.validation", "base.substate.mixin"]

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
