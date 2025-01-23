# Copyright 2025 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.osv import expression


class ImportMapping(models.Model):
    _inherit = "base_import.mapping"
    _rec_name = "column_name"

    mapping_template_id = fields.Many2one(
        comodel_name="base_import.mapping.template",
        ondelete="cascade",
    )
    pre_process_method = fields.Selection(
        [
            ("str_abs_value", "Absolute value (string)"),
            ("prefix_c", "Prefix C"),
            ("prefix_p", "Prefix P"),
        ]
    )
    mapped_value_ids = fields.Many2many(
        comodel_name="base_import.mapping.value.map",
        relation="base_import_mapping_value_map_rel",
        column1="mapping_id",
        column2="value_map_id",
    )
    python_code = fields.Char()
    # Convert to compute to manage from template if is set
    res_model = fields.Char(compute="_compute_res_model", store=True, readonly=False)

    @api.depends("mapping_template_id")
    def _compute_res_model(self):
        for line in self.filtered("mapping_template_id"):
            line.res_model = line.mapping_template_id.res_model

    @api.model
    def search(self, domain, offset=0, limit=None, order=None):
        domain = expression.AND(
            [
                domain,
                [
                    (
                        "mapping_template_id",
                        "=",
                        self.env.context.get("use_mapping_template_id", False),
                    )
                ],
            ]
        )
        return super().search(domain, offset=offset, limit=limit, order=order)

    @api.model_create_multi
    def create(self, vals_list):
        mapping_template_id = self.env.context.get("use_mapping_template_id", False)
        if mapping_template_id:
            for vals in vals_list:
                if "mapping_template_id" not in vals:
                    vals["mapping_template_id"] = mapping_template_id
        return super().create(vals_list)

    def pre_process_method_str_abs_value(self, value):
        return value.replace("-", "")

    def pre_process_method_prefix_c(self, value):
        return f"C-{value}"

    def pre_process_method_prefix_p(self, value):
        return f"P-{value}"
