# Migrated to v14.0 by Ashish Hirpara (https://www.ashish-hirpara.com)
# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from lxml import etree

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
        selection="_selection_type",
        required=True,
        default="filter",
    )
    filter_ids = fields.One2many(
        comodel_name="ir.filters", inverse_name="group_id", string="Filters"
    )
    insert_xpath = fields.Char(
        string="Insert XPath",
        help="XPath expression for the insertion point. "
        "Example: //search/filter[@name='my_filter']",
    )
    insert_position = fields.Selection(
        selection=[("before", "Before"), ("after", "After")],
        default="after",
        help="Insert the filter group before or after the element found by XPath.",
    )
    separator_position = fields.Selection(
        selection=[("before", "Before"), ("after", "After"), ("none", "None")],
        default="before",
        help="Where to place the separator relative to the filters. "
        "'None' to insert without a separator.",
    )

    @api.constrains("insert_xpath")
    def _check_insert_xpath(self):
        for rec in self:
            xpath = (rec.insert_xpath or "").strip()
            if not xpath:
                continue
            try:
                etree.XPath(xpath)
            except (etree.XPathSyntaxError, etree.XPathEvalError) as e:
                raise ValidationError(_("Invalid XPath:\n%s") % e) from e

    def unlink(self):
        self.filter_ids.unlink()
        return super().unlink()

    @api.model
    def _list_all_models(self):
        return self.env["ir.filters"]._list_all_models()
