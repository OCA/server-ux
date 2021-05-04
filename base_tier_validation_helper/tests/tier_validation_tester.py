# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TierValidationTester(models.Model):
    _name = 'tier.validation.tester'
    _inherit = ['tier.validation']

    state = fields.Selection(
        selection=[('draft', 'Draft'),
                   ('confirmed', 'Confirmed'),
                   ('cancel', 'Cancel')],
        default='draft',
    )
    test_field = fields.Float()
    user_id = fields.Many2one(string="Assigned to:",
                              comodel_name="res.users")

    @api.multi
    def action_confirm(self):
        self.write({'state': 'confirmed'})
