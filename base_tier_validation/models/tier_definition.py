# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class TierDefinition(models.Model):
    _name = "tier.definition"
    _description = "Tier Definition"

    @api.model
    def _get_default_name(self):
        return _("New Tier Validation")

    @api.model
    def _get_tier_validation_model_names(self):
        res = []
        return res

    name = fields.Char(
        string='Description',
        required=True,
        default=_get_default_name,
        translate=True,
    )
    model_id = fields.Many2one(
        comodel_name="ir.model",
        string="Referenced Model",
    )
    model = fields.Char(
        related='model_id.model', index=True, store=True,
    )
    review_type = fields.Selection(
        string="Validated by", default="individual",
        selection=[
            ("individual", "Specific user"),
            ("group", "Any user in a specific group."),
        ]
    )
    reviewer_id = fields.Many2one(
        comodel_name="res.users", string="Reviewer",
    )
    reviewer_group_id = fields.Many2one(
        comodel_name="res.groups", string="Reviewer group",
    )
    definition_type = fields.Selection(
        string="Definition",
        selection=[
            ('domain', 'Domain'),
        ],
        default='domain',
    )
    definition_domain = fields.Char()
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=30)
    company_id = fields.Many2one(
        comodel_name="res.company", string="Company",
        default=lambda self: self.env["res.company"]._company_default_get(
            "tier.definition"),
    )

    @api.onchange('model_id')
    def onchange_model_id(self):
        return {'domain': {
            'model_id': [
                ('model', 'in', self._get_tier_validation_model_names())]}}

    @api.onchange('review_type')
    def onchange_review_type(self):
        self.reviewer_id = None
        self.reviewer_group_id = None
