# Copyright 2024 ooops404
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import json

from lxml import etree

from odoo import api, fields, models


class CustomListViewLine(models.Model):
    _name = "custom.list.view.line"
    _description = "Custom List View Line"

    custom_list_view_id = fields.Many2one("custom.list.view")
    model_id = fields.Many2one(related="custom_list_view_id.model_id")
    model_name = fields.Char(related="custom_list_view_id.model_name")
    field_id = fields.Many2one("ir.model.fields", "New Field")
    after = fields.Many2one("ir.model.fields", "Place After")
    before = fields.Many2one("ir.model.fields", "Place Before")
    optional = fields.Selection([("show", "show"), ("hide", "hide")])
    label = fields.Char()
    use_widget = fields.Selection(
        [
            ("many2many_tags", "many2many_tags"),
            ("color", "color"),
            ("monetary", "monetary"),
        ],
        string="Widget",
        default=False,
    )
    fields_domain = fields.Char(
        compute="_compute_fields_domain",
        readonly=True,
        store=False,
    )

    @api.depends("custom_list_view_id.list_view_id")
    def _compute_fields_domain(self):
        for rec in self:
            arch = (
                rec.custom_list_view_id.original_arch
                or rec.custom_list_view_id.list_view_id.arch
            )
            doc = etree.XML(arch)
            nodes = doc.xpath("//tree//field")
            field_names = []
            for item in nodes:
                field_names.append(item.attrib["name"])
            field_ids = self.env["ir.model.fields"].search(
                [
                    ("model", "=", rec.custom_list_view_id.model_name),
                    ("name", "in", field_names),
                ]
            )
            rec.fields_domain = json.dumps([("id", "in", field_ids.ids)])
