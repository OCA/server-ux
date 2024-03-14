# © 2023 ForgeFlow, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import ast
import json as simplejson

from lxml import etree

from odoo import api, models


class Base(models.AbstractModel):
    _inherit = "base"

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        result = super(Base, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        if view_type in ["form", "tree", "kanban"]:
            # Get the current model name
            model_name = self._name

            # Fetch the configuration records for this model
            config_records = (
                self.env["field.access.right"]
                .sudo()
                .search(
                    [
                        ("model_id.model", "=", model_name),
                        "|",
                        ("group_ids", "in", self.env.user.groups_id.ids),
                        ("group_ids", "=", False),
                    ]
                )
            )
            doc = etree.XML(result["arch"])
            # Iterate through the configuration records
            for config in config_records:
                field_id = config.field_id
                # Find the field in the view's XML
                for node in doc.xpath(f"//field[@name='{field_id.name}']"):
                    attrs = ast.literal_eval(node.attrib.get("attrs", "{}"))
                    if config.readonly:
                        attrs["readonly"] = config.readonly == "yes" and True or False
                    if config.required:
                        attrs["required"] = config.required == "yes" and True or False
                    if config.invisible:
                        attrs["invisible"] = config.invisible == "yes" and True or False
                    if view_type == "tree":
                        attrs["column_invisible"] = (
                            config.invisible == "yes" and True or False
                        )
                    if config.readonly_domain:
                        attrs["readonly"] = config.readonly_domain
                    if config.required_domain:
                        attrs["required"] = config.required_domain
                    if config.invisible_domain:
                        attrs["invisible"] = config.invisible_domain
                    node.set("modifiers", simplejson.dumps(attrs))
                for node in doc.xpath(f"//label[@for='{field_id.name}']"):
                    attrs = ast.literal_eval(node.attrib.get("attrs", "{}"))
                    if config.invisible:
                        attrs["invisible"] = config.invisible == "yes" and True or False
                    if config.invisible_domain:
                        attrs["invisible"] = config.invisible_domain
                    node.set("modifiers", simplejson.dumps(attrs))
            result["arch"] = etree.tostring(doc)
        return result

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        model_name = self._name
        config_records = (
            self.env["field.access.right"]
            .sudo()
            .search(
                [
                    ("model_id.model", "=", model_name),
                    "|",
                    ("group_ids", "in", self.env.user.groups_id.ids),
                    ("group_ids", "=", False),
                ]
            )
        )
        res = super(Base, self).fields_get(allfields=allfields, attributes=attributes)
        for config in config_records:
            field_id = config.field_id
            if field_id.name in res:
                if config.exportable:
                    res[field_id.name]["exportable"] = (
                        config.exportable == "yes" and True or False
                    )
                if config.readonly:
                    res[field_id.name]["readonly"] = (
                        config.readonly == "yes" and True or False
                    )
                if config.required:
                    res[field_id.name]["required"] = (
                        config.required == "yes" and True or False
                    )
        return res
