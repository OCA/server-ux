# Copyright 2025 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import math

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class ImportMappingTemplate(models.Model):
    _inherit = ["base_import.import"]
    _name = "base_import.mapping.template"
    _description = "Template to group import mapping data"
    _transient = False
    _transient_max_hours = 0
    _transient_max_count = 0

    name = fields.Char()
    action_id = fields.Many2one(comodel_name="ir.actions.act_window")
    mapping_ids = fields.One2many(
        comodel_name="base_import.mapping",
        inverse_name="mapping_template_id",
    )
    forced_context = fields.Char(string="Context Value", default={}, required=True)
    forced_options = fields.Char(default={}, required=True)

    def execute_import_template(self):
        options = {
            "import_skip_records": [],
            "import_set_empty_fields": [],
            "fallback_values": {},
            "name_create_enabled_fields": {},
            "encoding": "",
            "separator": "",
            "quoting": '"',
            "date_format": "%Y-%m-%d",
            "datetime_format": "",
            "float_thousand_separator": ",",
            "float_decimal_separator": ".",
            "advanced": True,
            "has_headers": True,
            "keep_matches": False,
            "limit": 2000,
            "sheets": [],
            "sheet": "",
            "skip": 0,
            "tracking_disable": True,
        }
        eval_ctx = dict(self.env.context)
        ctx = {}
        if self.action_id:
            ctx.update(**safe_eval(self.action_id.context, eval_ctx))
        if self.forced_context != "{}":
            ctx.update(**safe_eval(self.forced_context, eval_ctx))
        self = self.with_context(**ctx)
        self.file = base64.b64decode(self.file)
        preview = self.parse_preview(options=options)
        if self.forced_options != "{}":
            options.update(**safe_eval(self.forced_options, eval_ctx))
        columns = [col.lower() for col in preview.get("headers", [])]
        fields = []
        for column in columns:
            line = self.mapping_ids.filtered(lambda x, col=column: x.column_name == col)
            fields.append(line.field_name)
        limit = options["limit"]
        steps_number = math.ceil((preview.get("file_length", 1) - 1) / limit)
        all_ids = []
        for step in range(steps_number):
            options["skip"] = step * limit
            options["limit"] = limit
            res = self.with_context(
                use_mapping_template_id=self.id, use_cached_db_id_for=True
            ).execute_import(fields, columns, options, dryrun=False)
            messages = res.get("messages", [])
            if messages:
                text_message = "\n".join(m.get("message", "") for m in messages)
                if step > 0:
                    text_message = (
                        f"Already imported {step * limit} records, but \n{text_message}"
                    )
                raise UserError(text_message)
            res_ids = res.get("ids", [])
            if not res_ids:
                raise UserError(_("No records were imported"))
            all_ids.extend(res_ids)
            # self.env.registry.clear_cache()
        self.file = False
        return self.action_view_imported_records(all_ids, ctx)

    @api.model
    def _convert_import_data(self, fields, options):
        data, import_fields = super()._convert_import_data(fields, options)
        if not self.env.context.get("use_mapping_template_id"):
            return data, import_fields
        multilevel = "id" in import_fields and any(
            "_ids/" in f for f in import_fields if f
        )
        if multilevel:
            id_index = import_fields.index("id")
        index_line_dict, index_column_dict = self.get_index_dictionaries(import_fields)
        # for index, field_name in enumerate(import_fields):
        # line = self.mapping_ids.filtered(
        #     lambda x, f_name=field_name: x.field_name == f_name
        # )
        for index, line in index_line_dict.items():
            field_name = line.field_name
            if line.pre_process_method:
                process_fnc = getattr(
                    line, f"pre_process_method_{line.pre_process_method}"
                )
                for row in data:
                    row[index] = process_fnc(row[index])
            elif line.python_code:
                self.update_data_with_python_code(
                    data, index, line.python_code, index_column_dict
                )
            elif field_name == "id":
                prefix = self.res_model.replace(".", "_")
                for row in data:
                    row[index] = f"{prefix}_{row[index]}_{self.id}"
            if line.mapped_value_ids:
                mapped_dict = {
                    map_line.value: map_line.new_value_ref
                    and str(map_line.new_value_ref.id)
                    or map_line.new_value
                    for map_line in line.mapped_value_ids
                }
                for row in data:
                    row[index] = mapped_dict.get(row[index], row[index])
            # Empty repeat values for principal record fields
            if multilevel and "_ids/" not in field_name:
                last_value = ""
                for row in data:
                    if row[id_index] in ("", last_value):
                        row[index] = ""
                    else:
                        last_value = row[id_index]
        return data, import_fields

    def get_index_dictionaries(self, import_fields):
        index_line_dict = {}
        index_column_dict = {}
        for index, field_name in enumerate(import_fields):
            line = self.mapping_ids.filtered(
                lambda x, f_name=field_name: x.field_name == f_name
            )
            index_line_dict[index] = line
            index_column_dict[index] = line.column_name
        return index_line_dict, index_column_dict

    def update_data_with_python_code(self, data, index, python_code, index_column_dict):
        for row in data:
            col_vals = {}
            if "col_vals" in python_code:
                for idx, col in index_column_dict.items():
                    col_vals[col] = row[idx]
            row[index] = safe_eval(
                python_code,
                {"value": row[index], "col_vals": col_vals},
            )

    def action_view_imported_records(self, res_ids, context=None):
        if self.action_id:
            action = self.env["ir.actions.actions"]._for_xml_id(self.action_id.xml_id)
        else:
            action = {
                "type": "ir.actions.act_window",
                "res_model": self.res_model,
                "name": _("Imported Records"),
                "views": [[False, "tree"], [False, "kanban"], [False, "form"]],
            }
        action["domain"] = [("id", "in", res_ids)]
        if context:
            action["context"] = context
        return action
