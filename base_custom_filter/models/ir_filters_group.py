# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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
        selection="_selection_type", string="Type", required=True, default="filter",
    )
    filter_ids = fields.One2many(
        comodel_name="ir.filters", inverse_name="group_id", string="Filters"
    )

    @api.constrains("model_id", "filter_ids")
    def _check_filter_group_model(self):
        for rec in self:
            if any(rec.filter_ids.filtered(lambda f: f.model_id != rec.model_id)):
                raise ValidationError(
                    _("The group contains filters related to different models.")
                )

    @api.constrains("type", "filter_ids")
    def _check_filter_group_type(self):
        for rec in self:
            if any(rec.filter_ids.filtered(lambda f: f.type != rec.type)):
                raise ValidationError(
                    _("The group contains filters of different types.")
                )

    @api.model
    def _list_all_models(self):
        self._cr.execute("SELECT model, name FROM ir_model ORDER BY name")
        return self._cr.fetchall()
