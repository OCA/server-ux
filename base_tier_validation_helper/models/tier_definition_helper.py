# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class TierDefinitionHelper(models.Model):
    _name = 'tier.definition.helper'
    _description = 'Tier Definition Helper'

    name = fields.Char(
        string='Description',
        required=True,
        default='New',
        translate=True,
    )
    model_id = fields.Many2one(
        comodel_name='ir.model',
        string='Model',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    model = fields.Char(
        related='model_id.model',
        string='Model Name',
        index=True,
        store=True,
    )
    review_type = fields.Selection(
        string='Validated by',
        selection=[
            ('individual', 'Specific user'),
            ('group', 'Any user in a specific group.'),
        ],
        default='individual',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    definition_type = fields.Selection(
        string='Definition',
        selection=[
            ('domain', 'Domain'),
        ],
        default='domain',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    definition_domain = fields.Char(
        string='Domain',
        help='Expressions can be any valid python expressions.'
             '(eg ["|", ("id", "=", 1), ("id", "=", "2")])',
    )
    notify_on_create = fields.Boolean(
        string='Notify Reviewers on Creation',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='If set, all possible reviewers will be notified by email when '
             'this definition is triggered.'
    )
    has_comment = fields.Boolean(
        string='Comment',
        default=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    approve_sequence = fields.Boolean(
        string='Approve by sequence',
        default=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='Approval order by the specified sequence number',
    )
    state = fields.Selection(
        string='Status',
        selection=[
            ('draft', 'Draft'),
            ('done', 'Done'),
        ],
        default='draft',
        index=True,
        copy=False,
        track_visibility='onchange',
        required=True,
        readonly=True,
    )
    line_ids = fields.One2many(
        comodel_name='tier.definition.helper.line',
        inverse_name='helper_id',
        string='Lines',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Name must be unique!')
    ]

    @api.multi
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        if 'name' not in default:
            default['name'] = _('%s (copy)') % (self.name)
        return super().copy(default=default)

    @api.onchange('model_id')
    def _onchange_model_id(self):
        models = self.env['tier.definition']._get_tier_validation_model_names()
        return {'domain': {'model_id': [('model', 'in', models)]}}

    @api.multi
    def button_create_tier(self):
        TierDefinition = self.env['tier.definition']
        for rec in self:
            if not rec.line_ids:
                raise ValidationError(_('Please add at least one line.'))
            for line in rec.line_ids:
                line.tier_definition_id = TierDefinition.create(
                    line._prepare_tier_definition())
            rec.write({'state': 'done'})

    @api.multi
    def button_delete_tier(self):
        self.mapped('line_ids').mapped('tier_definition_id').unlink()
        self.write({'state': 'draft'})


class TierDefinitionHelperLine(models.Model):
    _name = 'tier.definition.helper.line'
    _description = 'Tier Definition Helper Line'
    _order = 'approval_level'

    helper_id = fields.Many2one(
        comodel_name='tier.definition.helper',
        index=True,
        required=True,
        ondelete='cascade'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10
    )
    approval_level = fields.Integer(
        string='Level',
        default=1,
        required=True,
    )
    name = fields.Char(
        string='Name',
        default='New Tier Definition',
        required=True,
    )
    reviewer_id = fields.Many2one(
        comodel_name='res.users',
        string='Reviewer',
    )
    reviewer_group_id = fields.Many2one(
        comodel_name='res.groups',
        string='Reviewer group',
    )
    tier_definition_id = fields.Many2one(
        comodel_name='tier.definition',
        string='Tier Definition',
        readonly=True,
    )

    def _prepare_tier_definition(self):
        self.ensure_one()
        max_level = max(self.helper_id.line_ids.mapped('approval_level'))
        tier_definition = {
            'name': self.name,
            'model_id': self.helper_id.model_id.id,
            'sequence': max_level - self.approval_level,
            'review_type': self.helper_id.review_type,
            'definition_type': self.helper_id.definition_type,
            'notify_on_create': self.helper_id.notify_on_create,
            'has_comment': self.helper_id.has_comment,
            'approve_sequence': self.helper_id.approve_sequence,
        }
        # add reviewer by type
        if self.helper_id.review_type == 'individual':
            tier_definition['reviewer_id'] = self.reviewer_id.id
        elif self.helper_id.review_type == 'group':
            tier_definition['reviewer_group_id'] = self.reviewer_group_id.id
        # add domain
        if self.helper_id.definition_type == 'domain':
            tier_definition['definition_domain'] = self.helper_id.definition_domain
        return tier_definition
