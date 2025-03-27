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
    test_validation_field = fields.Integer(default=0)
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
    test_validation_field = fields.Float()
    user_id = fields.Many2one(string="Assigned to:", comodel_name="res.users")

    def action_confirm(self):
        self.write({"state": "confirmed"})


class TierValidationTester3(models.Model):
    _name = "tier.validation.tester3"
    _description = "Tier Validation Tester 3"
    _inherit = "tier.validation"
    _tier_validation_manual_config = False

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("cancel", "Cancel"),
        ],
        default="draft",
    )

    readonly_non_store_field = fields.Char(compute="_compute_readonly_non_store_field")
    readonly_store_field = fields.Char(
        compute="_compute_readonly_store_field", store=True
    )
    inverse_field = fields.Char(
        compute="_compute_inverse_field", inverse="_inverse_inverse_field", store=True
    )
    inverse_counter = fields.Integer(string="Counter", default=0)

    def _compute_readonly_non_store_field(self):
        """
        Assigns a default value to the non-store field.
        """
        for tester in self:
            tester.readonly_non_store_field = "Default Value"

    def _compute_readonly_field(self):
        """
        Assigns a default value, that the user won't be able to change in the views.
        """
        for tester in self:
            tester.readonly_store_field = "Default Value"

    def _compute_inverse_field(self):
        """
        Returns the readonly field value if none is present in the inverse field.
        """
        for tester in self:
            tester.inverse_field = tester.readonly_field

    def _inverse_inverse_field(self):
        """
        Any modification made to the field will increase by one the counter field
        """
        for tester in self:
            tester.inverse_counter += 1

    def action_confirm(self):
        self.write({"state": "confirmed"})


class TierValidationTesterComputed(models.Model):
    _name = "tier.validation.tester.computed"
    _description = "Tier Validation Tester Computed"
    _inherit = ["tier.validation"]
    _tier_validation_manual_config = False
    _tier_validation_state_field_is_computed = True

    confirmed = fields.Boolean()
    cancelled = fields.Boolean()
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("cancel", "Cancel"),
        ],
        compute="_compute_state",
        store=True,
    )
    test_field = fields.Float()
    test_validation_field = fields.Float()
    user_id = fields.Many2one(string="Assigned to:", comodel_name="res.users")

    @api.model
    def _get_after_validation_exceptions(self):
        return super()._get_after_validation_exceptions() + [
            "confirmed",
            "cancelled",
        ]

    @api.model
    def _get_under_validation_exceptions(self):
        return super()._get_under_validation_exceptions() + [
            "confirmed",
            "cancelled",
        ]

    @api.depends("confirmed", "cancelled")
    def _compute_state(self):
        for rec in self:
            if rec.cancelled:
                rec.state = "cancel"
            elif rec.confirmed:
                rec.state = "confirmed"
            else:
                rec.state = "draft"

    def action_confirm(self):
        self.write({"confirmed": True})

    def action_cancel(self):
        self.write({"cancelled": True})


class TierDefinition(models.Model):
    _inherit = "tier.definition"

    @api.model
    def _get_tier_validation_model_names(self):
        res = super()._get_tier_validation_model_names()
        res.append("tier.validation.tester")
        res.append("tier.validation.tester2")
        res.append("tier.validation.tester3")
        res.append("tier.validation.tester.computed")
        return res
