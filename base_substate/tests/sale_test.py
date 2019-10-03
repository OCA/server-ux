# Copyright 2020 Akretion Mourad EL HADJ MIMOUNE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models

from .models_mixin import TestMixin


class SaleTest(models.Model, TestMixin):
    _inherit = 'base.substate.mixin'
    _name = "base.substate.test.sale"
    _description = "Base substate Test Model"

    name = fields.Char(required=True)
    user_id = fields.Many2one('res.users', string='Responsible')
    state = fields.Selection(
        [('draft', 'New'), ('cancel', 'Cancelled'),
         ('sale', 'Sale'),
         ('done', 'Done')],
        string="Status", readonly=True, default='draft')
    active = fields.Boolean(default=True)
    partner_id = fields.Many2one('res.partner', string='Partner')
    line_ids = fields.One2many(
        comodel_name='base.substate.test.sale.line',
        inverse_name='sale_id',
        context={"active_test": False},
    )
    amount_total = fields.Float(
        compute='_compute_amount_total', store=True)

    @api.depends('line_ids')
    def _compute_amount_total(cls):
        for record in cls:
            for line in record.line_ids:
                record.amount_total += line.amount * line.qty

    @api.multi
    def button_confirm(cls):
        cls.write({'state': 'sale'})
        return True

    @api.multi
    def button_cancel(cls):
        cls.write({'state': 'cancel'})


class LineTest(models.Model, TestMixin):
    _name = "base.substate.test.sale.line"
    _description = "Base substate Test Model Line"

    name = fields.Char()
    sale_id = fields.Many2one(
        comodel_name='base.substate.test.sale',
        ondelete='cascade',
        context={"active_test": False},
    )
    qty = fields.Float()
    amount = fields.Float()
