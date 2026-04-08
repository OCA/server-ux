# Migrated to v14.0 by Ashish Hirpara (https://www.ashish-hirpara.com)
# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from lxml import etree

from odoo import api, models

_logger = logging.getLogger(__name__)


class Base(models.AbstractModel):
    _inherit = "base"

    @api.model
    def _user_has_access_to_item(self, item):
        if not item.group_ids:
            return True
        return bool(set(self.env.user.groups_id.ids) & set(item.group_ids.ids))

    @api.model
    def _insert_element(self, node, elem, position, is_root=False):
        if is_root:
            if position == "before":
                node.insert(0, elem)
            else:
                node.append(elem)
        elif position == "before":
            node.addprevious(elem)
        else:
            node.addnext(elem)

    @api.model
    def _get_default_filter_insertion_node(self, arch):
        return (
            arch.xpath("//search/filter[last()]")
            or arch.xpath("//search/field[last()]")
            or arch.xpath("//search")
        )

    @api.model
    def _get_custom_insertion_node(self, arch, xpath):
        if not xpath:
            return None
        try:
            return arch.xpath(xpath) or None
        except etree.XPathEvalError:
            _logger.warning("Invalid XPath expression: %s", xpath)
            return None

    @api.model
    def _build_filter_element(self, item, is_groupby=False):
        """Build a filter element for the search view."""
        attrs = {"name": f"ir_custom_filter_{item.id}", "string": item.name}
        if is_groupby:
            attrs["context"] = str({"group_by": item.groupby_field.sudo().name})
        else:
            if item.date_field:
                attrs["date"] = item.date_field.sudo().name
            else:
                attrs["domain"] = item.domain
        return etree.Element("filter", attrs)

    @api.model
    def _add_grouped_filters(self, res, custom_filters, group=None):
        arch = etree.fromstring(res["arch"])
        default_node = self._get_default_filter_insertion_node(arch)
        separator_added = False
        insert_xpath = group.insert_xpath if group else None
        insert_position = (group.insert_position if group else None) or "after"
        separator_position = (group.separator_position if group else None) or "before"
        first_inserted = None
        last_inserted = None
        custom_node = self._get_custom_insertion_node(arch, insert_xpath)
        for custom_filter in custom_filters:
            if not self._user_has_access_to_item(custom_filter):
                continue
            elem = self._build_filter_element(custom_filter)
            if custom_node:
                if last_inserted is not None:
                    # Insert after the last inserted element to maintain order
                    last_inserted.addnext(elem)
                else:
                    # First element: just insert the filter
                    self._insert_element(custom_node[0], elem, insert_position)
                    first_inserted = elem
                last_inserted = elem
            elif default_node:
                # Fall back to default behavior with separator
                if not separator_added:
                    is_root = default_node[0].tag == "search"
                    sep = etree.Element("separator")
                    self._insert_element(default_node[0], sep, "after", is_root)
                    separator_added = True
                sep_node = arch.xpath("//search/separator[last()]")
                if sep_node:
                    sep_node[0].addnext(elem)
        # Add separator based on separator_position
        if custom_node and first_inserted is not None and separator_position != "none":
            sep = etree.Element("separator")
            if separator_position == "before":
                first_inserted.addprevious(sep)
            else:
                last_inserted.addnext(sep)
        res["arch"] = etree.tostring(arch)
        return res

    @api.model
    def _get_default_groupby_insertion_node(self, arch):
        # Find the group that contains groupby filters
        return arch.xpath(
            "//search/group[.//filter[contains(@context, 'group_by')]]/filter[last()]"
        ) or arch.xpath("//search")

    @api.model
    def _add_grouped_groupby(self, res, custom_groupbys, group=None):
        arch = etree.fromstring(res["arch"])
        default_node = self._get_default_groupby_insertion_node(arch)
        insert_xpath = group.insert_xpath if group else None
        insert_position = (group.insert_position if group else None) or "after"
        last_inserted = None
        custom_node = self._get_custom_insertion_node(arch, insert_xpath)
        insertion_node = custom_node or default_node
        if not insertion_node:
            return res
        for custom_groupby in custom_groupbys:
            if not self._user_has_access_to_item(custom_groupby):
                continue
            elem = self._build_filter_element(custom_groupby, is_groupby=True)
            if last_inserted is not None:
                last_inserted.addnext(elem)
            else:
                is_root = insertion_node[0].tag in ("search", "group")
                self._insert_element(insertion_node[0], elem, insert_position, is_root)
            last_inserted = elem
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
                        res,
                        filter_group.filter_ids.sorted("sequence", True),
                        group=filter_group,
                    )
            if filters_no_group:
                for filter_no_group in filters_no_group:
                    res = self._add_grouped_filters(res, filter_no_group)
            # Add groupby type
            if groupby_groups:
                for groupby_group in groupby_groups:
                    res = self._add_grouped_groupby(
                        res,
                        groupby_group.filter_ids.sorted("sequence", True),
                        group=groupby_group,
                    )
            if groupbys_no_group:
                for groupby_no_group in groupbys_no_group:
                    res = self._add_grouped_groupby(res, groupby_no_group)
            if search_fields:
                res = self._add_search_field(res, search_fields)
        return res
