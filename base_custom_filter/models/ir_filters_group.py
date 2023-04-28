# Migrated to v14.0 by Ashish Hirpara (https://www.ashish-hirpara.com)
# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class IrFiltersGroup(models.Model):
    _name = "ir.filters.group"
    _description = "Filters Group"
    _order = "sequence, name, id"

    def _selection_type(self):
        return [("filter", "Filter"), ("groupby", "Group By")]

    sequence = fields.Integer()
    model_id = fields.Selection(
        selection="_list_all_models", string="Model", required=True
    )
    name = fields.Char(required=True, translate=True)
    type = fields.Selection(
        selection="_selection_type",
        required=True,
        default="filter",
    )
    filter_ids = fields.One2many(
        comodel_name="ir.filters", inverse_name="group_id", string="Filters"
    )

    def unlink(self):
        self.filter_ids.unlink()
        return super(IrFiltersGroup, self).unlink()

    @api.model
    def _list_all_models(self):
        return self.env["ir.filters"]._list_all_models()
