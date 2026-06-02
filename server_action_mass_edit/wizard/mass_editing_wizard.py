# Copyright (C) 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# Copyright (C) 2020 Iván Todorovich (https://twitter.com/ivantodorovich)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from lxml import etree

from odoo import api, fields, models


class MassEditingWizard(models.TransientModel):
    _name = "mass.editing.wizard"
    _description = "Wizard for mass edition"

    selected_item_qty = fields.Integer(readonly=True)
    remaining_item_qty = fields.Integer(readonly=True)
    operation_description_info = fields.Text(readonly=True)
    operation_description_warning = fields.Text(readonly=True)
    operation_description_danger = fields.Text(readonly=True)
    message = fields.Text(readonly=True)

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        server_action_id = self.env.context.get("server_action_id")
        server_action = self.env["ir.actions.server"].sudo().browse(server_action_id)
        active_ids = self.env.context.get("active_ids")

        if not server_action:
            return res

        original_active_ids = self.env.context.get("original_active_ids", active_ids)
        operation_description_info = False
        operation_description_warning = False
        operation_description_danger = False
        if len(active_ids) == len(original_active_ids):
            operation_description_info = self.env._(
                "The treatment will be processed on the %(amount)d selected record(s).",
                amount=len(active_ids),
            )
        elif len(original_active_ids):
            operation_description_warning = self.env._(
                "You have selected %(origin_amount)d "
                "record(s) that can not be processed.\n"
                "Only %(amount)d record(s) will be processed.",
                origin_amount=len(original_active_ids) - len(active_ids),
                amount=len(active_ids),
            )
        else:
            operation_description_danger = self.env._(
                "None of the %(amount)d record(s) you have selected can be processed.",
                amount=len(active_ids),
            )
        # Set values
        res.update(
            {
                "selected_item_qty": len(active_ids),
                "remaining_item_qty": len(original_active_ids),
                "operation_description_info": operation_description_info,
                "operation_description_warning": operation_description_warning,
                "operation_description_danger": operation_description_danger,
                "message": server_action.mass_edit_message,
            }
        )

        return res

    def onchange(self, values, field_names, fields_spec):
        # Make sure the values passed to the super cover the dynamic fields.
        # No onchanges are defined, but Odoo will call the onchange with empty
        # values for all fields when opening the wizard form view.
        first_call = not field_names
        if first_call:
            field_names = [fname for fname in values if fname != "id"]
            missing_names = [fname for fname in fields_spec if fname not in values]
            defaults = self.default_get(missing_names)
            for field_name in missing_names:
                values[field_name] = defaults.get(field_name, False)
                if field_name in defaults:
                    field_names.append(field_name)

        server_action_id = self.env.context.get("server_action_id")
        server_action = self.env["ir.actions.server"].sudo().browse(server_action_id)
        if not server_action:
            return super().onchange(values, field_names, fields_spec)

        # Collect dynamic field names to filter them out
        dynamic_field_names = set()
        for line in server_action.mapped("mass_edit_line_ids"):
            selection_field = "selection__" + line.field_id.name
            field_name = line.field_id.name
            dynamic_field_names.add(selection_field)
            dynamic_field_names.add(field_name)

            # Set default values for dynamic fields
            if selection_field not in values:
                values[selection_field] = "ignore"
            if field_name not in values:
                values[field_name] = False

        # Filter out dynamic fields before calling super
        filtered_values = {
            key: value
            for key, value in values.items()
            if key not in dynamic_field_names
        }
        filtered_field_names = [
            fname for fname in field_names if fname not in dynamic_field_names
        ]
        filtered_fields_spec = {
            fname: spec
            for fname, spec in fields_spec.items()
            if fname not in dynamic_field_names
        }

        res = super().onchange(
            filtered_values, filtered_field_names, filtered_fields_spec
        )

        # Ensure dynamic field values are included in the response
        if not res.get("value"):
            res["value"] = {}

        # Add dynamic field values to the result
        for field_name in dynamic_field_names:
            if field_name in values:
                res["value"][field_name] = values[field_name]

        view_temp = (
            self.env["ir.ui.view"]
            .sudo()
            .search([("name", "=", "Temporary Mass Editing Wizard")], limit=1)
        )
        if view_temp:
            view_temp.unlink()

        return res

    @api.model
    def _prepare_fields(self, line, field, field_info):
        result = {}
        # Add "selection field (set / add / remove / remove_m2m)
        if field.ttype == "many2many":
            selection = [
                ("ignore", self.env._("Don't touch")),
                ("set_m2m", self.env._("Set")),
                ("remove_m2m", self.env._("Remove")),
                ("add", self.env._("Add")),
            ]
        elif field.ttype == "one2many":
            selection = [
                ("ignore", self.env._("Don't touch")),
                ("set_o2m", self.env._("Set")),
                ("add_o2m", self.env._("Add")),
            ]
        else:
            selection = [
                ("ignore", self.env._("Don't touch")),
                ("set", self.env._("Set")),
                ("remove", self.env._("Remove")),
            ]
        result["selection__" + field.name] = {
            "type": "selection",
            "string": field_info["string"],
            "selection": selection,
        }
        # Add field info
        result[field.name] = field_info
        return result

    @api.model
    def _insert_field_in_arch(self, line, field, main_xml_group):
        etree.SubElement(
            main_xml_group,
            "label",
            {
                "for": "selection__" + field.name,
            },
        )
        div = etree.SubElement(
            main_xml_group,
            "div",
            {
                "class": "d-flex",
            },
        )
        etree.SubElement(
            div,
            "field",
            {
                "name": "selection__" + field.name,
                "modifiers": '{"required": true}',
                "class": "w-25",
            },
        )
        field_vals = self._get_field_options(field)
        if line.widget_option:
            field_vals["widget"] = line.widget_option
        field_element = etree.SubElement(div, "field", field_vals)
        if field.ttype == "one2many":
            comodel = self.env[field.relation]
            dummy, form_view = comodel._get_view(view_type="form")
            dummy, list_view = comodel._get_view(view_type="list")
            field_context = {}
            if form_view:
                field_context["form_view_ref"] = form_view.xml_id
            if list_view:
                field_context["list_view_ref"] = list_view.xml_id
            if field_context:
                field_element.attrib["context"] = json.dumps(field_context)
            else:
                model_arch, dummy = self.env[field.model]._get_view(view_type="form")
                embedded_list = None
                for node in model_arch.xpath(f"//field[@name='{field.name}'][./list]"):
                    embedded_list = node.xpath("./list")[0]
                    break
                if embedded_list is not None:
                    for node in embedded_list.xpath("./*"):
                        modifiers = node.get("modifiers")
                        if modifiers:
                            node.attrib["modifiers"] = modifiers
                    field_element.insert(0, embedded_list)

        return field_element

    def _get_field_options(self, field):
        return {
            "name": field.name,
            "invisible": f'selection__{field.name} in ["ignore", "remove", False]',
            "class": "w-75",
        }

    @api.model
    def get_views(self, views, options=None):
        for view, _type in views:
            if view:
                view = self.env["ir.ui.view"].sudo().browse(view)
                server_action = view.mass_server_action_id
                self = self.with_context(server_action_id=server_action.id)
        return super().get_views(views, options)

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        view = self.env["ir.ui.view"].sudo().browse(view_id)
        server_action = view.mass_server_action_id
        self = self.with_context(server_action_id=server_action.id)
        if not server_action:
            return super().get_view(view_id, view_type, **options)
        result = super().get_view(view_id, view_type, **options)
        arch = etree.fromstring(result["arch"])
        main_xml_group = arch.find('.//group[@name="group_field_list"]')
        for line in server_action.mapped("mass_edit_line_ids"):
            self._insert_field_in_arch(line, line.field_id, main_xml_group)
            if line.field_id.ttype == "one2many":
                comodel = self.env[line.field_id.relation]
                result["models"] = dict(
                    result["models"], **{comodel._name: tuple(comodel.fields_get())}
                )
        result["arch"] = etree.tostring(arch, encoding="unicode")
        return result

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        server_action_id = self.env.context.get("server_action_id")
        server_action = self.env["ir.actions.server"].sudo().browse(server_action_id)
        if not server_action:
            return super().fields_get(allfields, attributes)
        res = super().fields_get(allfields, attributes)
        fields_info = self.env[server_action.model_id.model].fields_get()
        for line in server_action.mapped("mass_edit_line_ids"):
            field = line.field_id
            field_info = self._clean_check_company_field_domain(
                self.env[server_action.model_id.model], field, fields_info[field.name]
            )
            field_info["relation_field"] = False
            if line.field_domain:
                field_info["domain"] = line.field_domain
            elif not line.apply_domain and "domain" in field_info:
                field_info["domain"] = "[]"
            res.update(self._prepare_fields(line, field, field_info))
        return res

    @api.model
    def _clean_check_company_field_domain(self, TargetModel, field, field_info):
        """
        This method remove the field view domain added by Odoo for relational
        fields with check_company attribute to avoid error for non exists
        company_id or company_ids fields in wizard view.
        See _description_domain method in _Relational Class
        """
        field_class = TargetModel._fields[field.name]
        if not field_class.relational or not field_class.check_company or field.domain:
            return field_info
        field_info["domain"] = "[]"
        return field_info

    @api.model_create_multi
    def create(self, vals_list):
        server_action_id = self.env.context.get("server_action_id")
        server_action = self.env["ir.actions.server"].sudo().browse(server_action_id)
        if server_action:
            for vals in vals_list:
                values = {}
                for key, val in vals.items():
                    if key.startswith("selection_"):
                        split_key = key.split("__", 1)[1]
                        if val == "set" or val == "add_o2m":
                            values.update({split_key: vals.get(split_key, False)})

                        elif val == "set_o2m" or val == "set_m2m":
                            values.update(
                                {split_key: [(6, 0, [])] + vals.get(split_key, [])}
                            )

                        elif val == "remove":
                            values.update({split_key: False})

                        elif val == "remove_m2m":
                            m2m_list = []
                            if vals.get(split_key):
                                for m2m_id in vals.get(split_key, False):
                                    m2m_list.append((3, m2m_id[1]))
                            if m2m_list:
                                values.update({split_key: m2m_list})
                            else:
                                values.update({split_key: [(5, 0, [])]})

                        elif val == "add":
                            values.update({split_key: vals.get(split_key, False)})

                if values:
                    self._exec_write(server_action, values)
        return super().create([{}])

    def _exec_write(self, server_action, vals):
        active_ids = self.env.context.get("active_ids", [])
        model = self.env[server_action.model_id.model].with_context(mass_edit=True)
        records = model.browse(active_ids)
        records.write(vals)

    def _prepare_create_values(self, vals_list):
        return vals_list

    def read(self, fields=None, load="_classic_read"):
        """Without this call, dynamic fields build by fields_view_get()
        generate a log warning, i.e.:
        odoo.models:mass.editing.wizard.read() with unknown field 'myfield'
        odoo.models:mass.editing.wizard.read()
            with unknown field 'selection__myfield'
        """
        # When fields=None or fields=[], we need to explicitly provide only real fields
        # because dynamic fields may be in the record cache but not in _fields
        if fields is None or fields == []:
            # Provide only the real model fields
            real_fields = list(self._fields.keys())
        else:
            # Filter out dynamic fields that are not in _fields
            real_fields = [x for x in fields if x in self._fields]

        result = super().read(real_fields, load=load)

        # Add back the requested dynamic fields with False value
        if fields and fields != [] and result:
            for x in fields:
                if x not in real_fields:
                    result[0].update({x: False})
        return result

    def button_apply(self):
        self.ensure_one()
