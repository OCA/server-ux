# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Pedro M. Baeza
# Copyright 2022 Tecnativa - Víctor Martínez
# Copyright 2023 Amitaujas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from lxml import etree

from odoo import api, models


class Base(models.AbstractModel):
    _inherit = "base"

    @api.model
    def _add_custom_filters(self, res, custom_filters):
        arch = etree.fromstring(res["arch"])
        for custom_filter in custom_filters:
            node = False
            if custom_filter.position_after:
                node = arch.xpath("//field[@name='%s']" % custom_filter.position_after)
            if not node:
                node = arch.xpath("//field[last()]")
            if node:
                elem = etree.Element(
                    "field",
                    {"name": custom_filter.expression, "string": custom_filter.name},
                )
                node[0].addnext(elem)
        res["arch"] = etree.tostring(arch)
        return res

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        """Inject fields field in search views."""
        res = super().get_view(view_id, view_type, **options)
        if view_type == "search":
            custom_filters = self.env["ir.ui.custom.field.filter"].search(
                [("model_name", "=", res.get("model"))]
            )
            if custom_filters:
                res = self._add_custom_filters(res, custom_filters)
        return res

    @api.model
    def get_views(self, views, options=None):
        """Inject fake field definition for having custom filters available."""
        res = super().get_views(views, options)
        custom_filters = self.env["ir.ui.custom.field.filter"].search(
            [("model_name", "=", self._name)]
        )
        for custom_filter in custom_filters:
            field = custom_filter._get_related_field()
            field_name = custom_filter.expression
            res["models"][self._name][field_name] = field.get_description(self.env)
            # force this for avoiding to appear on the rest of the UI
            res["models"][self._name][field_name]["selectable"] = False
            res["models"][self._name][field_name]["sortable"] = False
            res["models"][self._name][field_name]["store"] = False
        return res
