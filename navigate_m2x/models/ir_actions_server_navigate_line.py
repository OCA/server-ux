# Copyright (C) 2020 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class IrActionsServerNavigateLine(models.Model):
    _name = "ir.actions.server.navigate.line"
    _description = "Server Actions Navigation Lines"
    _order = "sequence"

    sequence = fields.Integer(string="Sequence", default=9999)

    sequence2 = fields.Integer(
        related='sequence',
        string="Line Number",
        readonly=True,
        store=True,
    )

    field_model = fields.Char(
        string="Model", related="field_id.relation", store=True)

    action_id = fields.Many2one(
        comodel_name="ir.actions.server", string="Action",
        required=True, ondelete="cascade")

    field_id = fields.Many2one(
        comodel_name="ir.model.fields", string="Field",
        required=True)
