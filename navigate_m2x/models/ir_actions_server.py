# Copyright (C) 2020 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class IrActionsServer(models.Model):
    _inherit = "ir.actions.server"

    state = fields.Selection(selection_add=[("navigate_m2x", "Navigate")])

    navigate_action_id = fields.Many2one(
        string="Navigation Action",
        comodel_name='ir.actions.act_window',
        domain="[('res_model', '=', max_navigate_line_model)]",
        help="Define here the action used when the navigation will be executed"
        " if empty, a generic action will be used.")

    navigate_line_ids = fields.One2many(
        comodel_name="ir.actions.server.navigate.line",
        string="Navigate Lines", inverse_name="action_id")

    max_navigate_line_sequence = fields.Integer(
        string='Max Navigate sequence in lines',
        compute='_compute_max_navigate_line',
        store=True
    )

    max_navigate_line_model = fields.Char(
        string="Max Navigate Model in lines",
        compute="_compute_max_navigate_line",
        store=True)

    @api.depends("navigate_line_ids", "model_id")
    def _compute_max_navigate_line(self):
        """Allow to know the highest sequence entered in navigate lines.
        Then we add 1 to this value for the next sequence.
        This value is given to the context of the o2m field in the view.
        So when we create new navigate line, the sequence is automatically
        added as :  max_sequence + 1
        """
        for action in self:
            action.max_navigate_line_sequence = (
                max(action.mapped('navigate_line_ids.sequence') or [0]) + 1)
            action.max_navigate_line_model =\
                action.navigate_line_ids\
                and action.navigate_line_ids[-1].field_model\
                or action.model_id.model

    def delete_last_line(self):
        self.ensure_one()
        self.navigate_line_ids[-1].unlink()
        self.navigate_action_id = False

    @api.model
    def run_action_navigate_m2x_multi(self, action, eval_context=None):
        IrModel = self.env['ir.model']
        lines = action.navigate_line_ids
        if len(lines) == 0:
            raise UserError(_(
                "The Action Server %s is not correctly set\n"
                " : No fields defined"))
        mapped_field_value = ".".join(lines.mapped("field_id.name"))

        item_ids = eval_context['records'].mapped(mapped_field_value).ids
        domain = "[('id','in',[" + ','.join(map(str, item_ids)) + "])]"

        # Use Defined action if defined
        if action.navigate_action_id:
            return_action = action.navigate_action_id
            result = return_action.read()[0]
            result['domain'] = domain
        else:
            # Otherwise, return a default action
            model_name = action.max_navigate_line_model
            model = IrModel.search([('model', '=', model_name)])
            view_mode = 'tree,form'
            result = {
                'name': model.name,
                'domain': domain,
                'res_model': model_name,
                'target': 'current',
                'type': 'ir.actions.act_window',
                'view_mode': view_mode,
            }

        return result
