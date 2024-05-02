# Copyright 2024 ooops404
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from lxml import etree

from odoo import api, fields, models


class CustomListView(models.Model):
    _name = "custom.list.view"
    _description = "Custom List View"

    active = fields.Boolean(default=True)
    name = fields.Char(required=True)
    model_id = fields.Many2one("ir.model", required=True, ondelete="cascade")
    model_name = fields.Char(related="model_id.model", store=True)
    list_view_id = fields.Many2one("ir.ui.view", required=True)
    line_ids = fields.One2many("custom.list.view.line", "custom_list_view_id")
    original_arch = fields.Text(readonly=True)

    _sql_constraints = [
        (
            "unique_model_list_view_rec",
            "UNIQUE(list_view_id)",
            "Only one record per view is allowed. "
            "Please modify existing record instead.",
        )
    ]

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        for rec in recs:
            rec.original_arch = rec.list_view_id.arch
        return recs

    def button_apply_changes(self):
        self.ensure_one()
        doc = etree.XML(self.original_arch)
        for mod_line in self.line_ids:
            target = mod_line.before and mod_line.before.name or mod_line.after.name
            for node in doc.xpath("/tree/field[@name='%s']" % target):
                node_string = (
                    "<field name='%s' widget='%s' optional='%s' string='%s'/>"
                    % (
                        mod_line.field_id.name,
                        mod_line.use_widget or "",
                        mod_line.optional or "",
                        mod_line.label or mod_line.field_id.field_description,
                    )
                )
                new_node = etree.fromstring(node_string)
                if mod_line.before:
                    node.addprevious(new_node)
                else:
                    node.addnext(new_node)
        new_arch = etree.tostring(doc, encoding="unicode").replace("\t", "")
        self.list_view_id.arch = new_arch

    def button_roll_back(self):
        self.ensure_one()
        doc = etree.XML(self.original_arch)
        new_arch = etree.tostring(doc, encoding="unicode").replace("\t", "")
        self.list_view_id.arch = new_arch
