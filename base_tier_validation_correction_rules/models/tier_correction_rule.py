# Copyright 2026 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class TierCorrectionRule(models.Model):
    _name = "tier.correction.rule"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Correction Rules"
    _rec_name = "model_id"

    model_id = fields.Many2one(
        comodel_name="ir.model",
        string="Referenced Model",
        domain=lambda self: [
            (
                "model",
                "in",
                self.env["tier.definition"]._get_tier_validation_model_names(),
            )
        ],
    )
    line_ids = fields.One2many(
        comodel_name="tier.correction.rule.line",
        inverse_name="rule_id",
    )


class TierCorrectionRuleLine(models.Model):
    _name = "tier.correction.rule.line"
    _description = "Correction Rules Line"
    _order = "sequence"

    rule_id = fields.Many2one(
        comodel_name="tier.correction.rule",
        index=True,
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer(required=True, default=10)
    model = fields.Char(
        related="rule_id.model_id.model",
        store=True,
    )
    reviewer_from_ids = fields.Many2many(
        comodel_name="res.users",
        relation="tier_correction_from_res_users_rel",
        column1="reviewer_from_id",
        column2="user_id",
        required=True,
        index=True,
        string="Users",
    )
    reviewer_to_ids = fields.Many2many(
        comodel_name="res.users",
        relation="tier_correction_to_res_users_rel",
        column1="reviewer_to_id",
        column2="user_id",
        string="Allowed Reviewers",
    )
