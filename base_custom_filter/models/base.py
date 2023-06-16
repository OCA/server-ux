# Migrated to v14.0 by Ashish Hirpara (https://www.ashish-hirpara.com)
# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from lxml import etree

from odoo import api, models


class Base(models.AbstractModel):
    _inherit = "base"

    @api.model
    def _user_has_access_to_item(self, item):
        if not item.group_ids:
            return True
        return bool(set(self.env.user.groups_id.ids) & set(item.group_ids.ids))

    @api.model
    def _add_grouped_filters(self, res, custom_filters):
        arch = etree.fromstring(res["arch"])
        node = arch.xpath("//search/filter[last()]")
        if node:
            node[0].addnext(etree.Element("separator"))
            for custom_filter in custom_filters:
                if not self._user_has_access_to_item(custom_filter):
                    continue
                node = arch.xpath("//search/separator[last()]")
                if node:
                    elem = etree.Element(
                        "filter",
                        {
                            "name": "ir_custom_filter_%s" % custom_filter.id,
                            "string": custom_filter.name,
                            "domain": custom_filter.domain,
                        },
                    )
                    node[0].addnext(elem)
        res["arch"] = etree.tostring(arch)
        return res

    @api.model
    def _add_grouped_groupby(self, res, custom_groupbys):
        arch = etree.fromstring(res["arch"])
        node = arch.xpath("//group/filter[last()]")
        if node:
            node[0].addnext(etree.Element("separator"))
            for custom_groupby in custom_groupbys:
                if not self._user_has_access_to_item(custom_groupby):
                    continue
                node = arch.xpath("//group/separator[last()]")
                if node:
                    elem = etree.Element(
                        "filter",
                        {
                            "name": "ir_custom_filter_%s" % custom_groupby.id,
                            "string": custom_groupby.name,
                            "context": str(
                                {"group_by": custom_groupby.groupby_field.name}
                            ),
                        },
                    )
                    node[0].addnext(elem)
        res["arch"] = etree.tostring(arch)
        return res

    @api.model
    def _add_search_field(self, res, search_fields):
        xml_arch = etree.fromstring(res["arch"])
        for search_field in search_fields:
            if not self._user_has_access_to_item(search_field):
                continue
            new_field = etree.Element(
                "field",
                name=search_field.search_field_id.sudo().name,
            )
            if search_field.filter_domain:
                new_field.set("filter_domain", search_field.filter_domain)
            xml_arch.append(new_field)
        res["arch"] = etree.tostring(xml_arch)
        return res

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        """Add filters in search views."""
        res = super().get_view(view_id=view_id, view_type=view_type, **options)
        if view_type == "search":
            filter_groups = self.env["ir.filters.group"].search(
                [
                    ("model_id", "=", res.get("model")),
                    ("filter_ids", "!=", False),
                    ("type", "=", "filter"),
                ]
            )
            filters_no_group = self.env["ir.filters"].search(
                [
                    ("model_id", "=", res.get("model")),
                    ("group_id", "=", False),
                    ("type", "=", "filter"),
                ],
                order="sequence desc",
            )
            groupby_groups = self.env["ir.filters.group"].search(
                [
                    ("model_id", "=", res.get("model")),
                    ("filter_ids", "!=", False),
                    ("type", "=", "groupby"),
                ]
            )
            groupbys_no_group = self.env["ir.filters"].search(
                [
                    ("model_id", "=", res.get("model")),
                    ("group_id", "=", False),
                    ("type", "=", "groupby"),
                ],
                order="sequence desc",
            )
            search_fields = self.env["ir.filters"].search(
                [
                    ("model_id", "=", res.get("model")),
                    ("type", "=", "search"),
                ],
                order="sequence desc",
            )
            # Add filter type
            if filter_groups:
                for filter_group in filter_groups:
                    res = self._add_grouped_filters(
                        res, filter_group.filter_ids.sorted("sequence", True)
                    )
            if filters_no_group:
                for filter_no_group in filters_no_group:
                    res = self._add_grouped_filters(res, filter_no_group)
            # Add groupby type
            if groupby_groups:
                for groupby_group in groupby_groups:
                    res = self._add_grouped_groupby(
                        res, groupby_group.filter_ids.sorted("sequence", True)
                    )
            if groupbys_no_group:
                for groupby_no_group in groupbys_no_group:
                    res = self._add_grouped_groupby(res, groupby_no_group)
            if search_fields:
                res = self._add_search_field(res, search_fields)
        return res
