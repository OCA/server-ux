# Copyright 2026 Camptocamp SA
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class LineNumberingTestOrder(models.Model):
    _name = "line.numbering.test.order"
    _inherit = ["line.numbering.mixin"]
    _description = "Line numbering test order"

    _line_field = "line_ids"
    _line_position_field = "position"

    name = fields.Char()
    line_ids = fields.One2many("line.numbering.test.line", "order_id")


class LineNumberingTestLine(models.Model):
    _name = "line.numbering.test.line"
    _description = "Line numbering test line"
    _order = "sequence, id"

    order_id = fields.Many2one("line.numbering.test.order", ondelete="cascade")
    sequence = fields.Integer(default=10)
    name = fields.Char()
    position = fields.Char()
