# Copyright 2025 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ImportMappingValueMap(models.Model):
    _name = "base_import.mapping.value.map"
    _description = "Map import value with odoo value"
    _rec_name = "value"

    mapping_ids = fields.Many2many(
        comodel_name="base_import.mapping",
        relation="base_import_mapping_value_map_rel",
        column1="value_map_id",
        column2="mapping_id",
    )
    value = fields.Char()
    new_value = fields.Char()
    new_value_ref = fields.Reference(
        lambda self: [
            (m.model, m.name) for m in self.env["ir.model"].sudo().search([])
        ],
        string="Object",
    )
