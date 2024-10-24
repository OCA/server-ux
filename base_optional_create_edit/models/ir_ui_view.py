# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import api, models


class Model(models.AbstractModel):
    _inherit = "base"

    @api.model
    def get_views(self, views, options=None):
        res = super().get_views(views, options)
        view_form = res.get("views", {}).get("form", {}).get("arch")
        if view_form:
            tree = etree.fromstring(view_form)
            view_fields = set(tree.xpath(".//field[not(ancestor::field)]"))

            comodel_names = list(
                {
                    model.comodel_name
                    for field_name, model in self._fields.items()
                    if model.relational
                }
            )
            domain = [("avoid_create_edit", "=", True), ("model", "in", comodel_names)]
            relational_models = self.env["ir.model"].sudo().search(domain)
            relational_models_names = relational_models.mapped("model")
            field_names = [
                field_name
                for field_name, model in self._fields.items()
                if relational_models_names
                and model.comodel_name
                and model.comodel_name in relational_models_names
            ]

            for view_field in view_fields:
                if view_field.attrib["name"] in field_names:
                    view_field.set("can_create", "false")
                    view_field.set("can_write", "false")
                    view_field.set("no_create", "true")
                    view_field.set("no_edit", "true")

            view_form = etree.tostring(tree)
            res["views"]["form"]["arch"] = view_form
        return res
