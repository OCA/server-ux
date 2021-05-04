# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TierDefinitionHelper(models.Model):
    _inherit = 'tier.definition.helper'
    _description = 'Tier Definition Helper'

    review_type = fields.Selection(
        selection_add=[('expression', 'Python Expression')]
    )
    is_reviewers = fields.Boolean(
        string='Reviewers',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='Check this if you want to select many reviewers.',
    )
    definition_type = fields.Selection(
        selection_add=[('formula', 'Formula')]
    )
    is_amount_domain = fields.Boolean(
        string='Amount',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='Check this if you want to use domain with range of amount.',
    )
    amount_ref_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Amount Reference',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    condition_type = fields.Selection([
        ('range', 'Range'),
        ('min', 'Minimum Amount'),
        ('max', 'Maximum Amount')],
        string='Condition Type',
        default='range',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    @api.onchange('model_id')
    def _onchange_ref(self):
        return {'domain': {
            'amount_ref_id': [
                ('model', '=', self.model_id.model),
                ('ttype', 'in', ('float', 'monetary'))
            ],
        }}

    @api.onchange('review_type')
    def _onchange_review_type(self):
        if self.review_type != 'expression':
            self.write({'is_reviewers': False})

    @api.onchange('definition_type')
    def _onchange_definition_type(self):
        if self.definition_type != 'formula':
            self.write({'is_amount_domain': False})


class TierDefinitionHelperLine(models.Model):
    _inherit = 'tier.definition.helper.line'

    reviewer_expression = fields.Text(
        string='Review Expression',
        help="Write Python code that defines the reviewer. "
             "The result of executing the expression must be a res.users "
             "recordset.",
    )
    reviewer_ids = fields.Many2many(
        comodel_name='res.users',
        string='Reviewers',
    )
    python_code = fields.Text(
        string='Tier Definition Expression',
        help="Write Python code that defines when this tier confirmation "
             "will be needed. The result of executing the expresion must be "
             "a boolean.",
    )
    min_amount = fields.Float(
        string='Minimum Amount',
        default=0.00,
    )
    max_amount = fields.Float(
        string='Maximum Amount',
        default=0.00,
    )

    def _get_reviewer_expression(self):
        self.ensure_one()
        reviewer_expression = self.reviewer_expression
        if self.helper_id.is_reviewers:
            reviewer_expression = "rec.env['res.users']."\
                "search([('id', 'in', %s)])" % self.reviewer_ids.mapped('id')
        self.reviewer_expression = reviewer_expression
        return reviewer_expression

    def _get_python_code(self):
        self.ensure_one()
        python_code = self.python_code
        # Add domain with amount
        if self.helper_id.is_amount_domain:
            python_code = ""
            if self.helper_id.condition_type in ('range', 'min'):
                python_code += "rec.%s >= %s" \
                    % (self.helper_id.amount_ref_id.name, str(self.min_amount))
            if self.helper_id.condition_type in ('range', 'max'):
                python_code += " and " if python_code != "" else ""
                python_code += "rec.%s <= %s" \
                    % (self.helper_id.amount_ref_id.name, str(self.max_amount))
        self.python_code = python_code
        return python_code

    def _prepare_tier_definition(self):
        self.ensure_one()
        tier_definition = super()._prepare_tier_definition()
        # add reviewer by type
        if self.helper_id.review_type == 'expression':
            tier_definition['reviewer_expression'] = self._get_reviewer_expression()
        # add domain
        if self.helper_id.definition_type == 'formula':
            tier_definition['python_code'] = self._get_python_code()
        return tier_definition
