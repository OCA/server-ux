# Copyright (C) 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# Copyright (C) 2020 Iván Todorovich (https://twitter.com/ivantodorovich)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import _, api, fields, models


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
        # Compute items quantity
        # Compatibility with server_actions_domain
        active_ids = self.env.context.get("active_ids")
        original_active_ids = self.env.context.get("original_active_ids", active_ids)
        # Compute operation messages
        operation_description_info = False
        operation_description_warning = False
        operation_description_danger = False
        if len(active_ids) == len(original_active_ids):
            operation_description_info = _(
                "The treatment will be processed on the %d selected record(s)."
            ) % (len(active_ids))
        elif len(original_active_ids):
            operation_description_warning = _(
                "You have selected %d record(s) that can not be processed.\n"
                "Only %d record(s) will be processed."
            ) % (
                len(original_active_ids) - len(active_ids),
                len(active_ids),
            )
        else:
            operation_description_danger = _(
                "None of the %d record(s) you have selected can be processed."
            ) % (len(active_ids))
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

    @api.model
    def _prepare_fields(self, line, field, field_info):
        result = {}
        # Add "selection field (set / add / remove / remove_m2m)
        if field.ttype == "many2many":
            selection = [
                ("set", _("Set")),
                ("remove_m2m", _("Remove")),
                ("add", _("Add")),
            ]
        elif field.ttype == "one2many":
            selection = [
                ("set_o2m", _("Set")),
                ("remove_o2m", _("Remove")),
            ]
        else:
            selection = [("set", _("Set")), ("remove", _("Remove"))]
        result["selection__" + field.name] = {
            "type": "selection",
            "string": field_info["string"],
            "selection": selection,
        }
        # Add field info
        result[field.name] = field_info
        # Patch fields with required extra data
        for item in result.values():
            item.setdefault("views", {})
        return result

    @api.model
    def _insert_field_in_arch(self, line, field, main_xml_group):
        etree.SubElement(
            main_xml_group,
            "field",
            {"name": "selection__" + field.name, "colspan": "2"},
        )
        field_vals = self._get_field_options(field)
        if line.widget_option:
            field_vals["widget"] = line.widget_option
        etree.SubElement(main_xml_group, "field", field_vals)

    def _get_field_options(self, field):
        return {"name": field.name, "nolabel": "1", "colspan": "4"}

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        result = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )

        server_action_id = self.env.context.get("server_action_id")
        server_action = self.env["ir.actions.server"].sudo().browse(server_action_id)
        if not server_action:
            return result

        all_fields = {}
        TargetModel = self.env[server_action.model_id.model]
        fields_info = TargetModel.fields_get()

        arch = etree.fromstring(result["arch"])

        main_xml_group = arch.find('.//group[@name="group_field_list"]')

        for line in server_action.mapped("mass_edit_line_ids"):
            # Field part
            field = line.field_id
            field_info = self._clean_check_company_field_domain(
                TargetModel, field, fields_info[field.name]
            )
            if not line.apply_domain and "domain" in field_info:
                field_info["domain"] = "[]"
            all_fields.update(self._prepare_fields(line, field, field_info))
            # XML Part
            self._insert_field_in_arch(line, field, main_xml_group)
        result["arch"] = etree.tostring(arch, encoding="unicode")
        result["fields"] = all_fields
        return result

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

    @api.model
    def create(self, vals):
        server_action_id = self.env.context.get("server_action_id")
        server_action = self.env["ir.actions.server"].sudo().browse(server_action_id)
        active_ids = self.env.context.get("active_ids", [])
        if server_action and active_ids:
            TargetModel = self.env[server_action.model_id.model]
            IrModelFields = self.env["ir.model.fields"]
            IrTranslation = self.env["ir.translation"]

            values = {}
            for key, val in vals.items():
                if key.startswith("selection_"):
                    split_key = key.split("__", 1)[1]
                    if val == "set":
                        values.update({split_key: vals.get(split_key, False)})

                    elif val == "set_o2m":
                        values.update({
                            split_key: vals.get(split_key, [(6, 0, [])])})

                    elif val == "remove":
                        values.update({split_key: False})
                        # If field to remove is translatable,
                        # its translations have to be removed
                        model_field = IrModelFields.search(
                            [
                                ("model", "=", server_action.model_id.model),
                                ("name", "=", split_key),
                            ]
                        )
                        if model_field and model_field.translate:
                            translations = IrTranslation.search(
                                [
                                    ("res_id", "in", active_ids),
                                    ("type", "=", "model"),
                                    (
                                        "name",
                                        "=",
                                        u"{},{}".format(
                                            server_action.model_id.model, split_key
                                        ),
                                    ),
                                ]
                            )
                            translations.unlink()

                    elif val == "remove_m2m":
                        m2m_list = []
                        if vals.get(split_key):
                            for m2m_id in vals.get(split_key)[0][2]:
                                m2m_list.append((3, m2m_id))
                        if m2m_list:
                            values.update({split_key: m2m_list})
                        else:
                            values.update({split_key: [(5, 0, [])]})

                    elif val == "remove_o2m":
                        values.update({split_key: [(6, 0, [])]})

                    elif val == "add":
                        m2m_list = []
                        for m2m_id in vals.get(split_key, False)[0][2]:
                            m2m_list.append((4, m2m_id))
                        values.update({split_key: m2m_list})
            if values:
                TargetModel.browse(active_ids).write(values)
        return super().create({})

    def read(self, fields, load="_classic_read"):
        """Without this call, dynamic fields build by fields_view_get()
        generate a log warning, i.e.:
        odoo.models:mass.editing.wizard.read() with unknown field 'myfield'
        odoo.models:mass.editing.wizard.read()
            with unknown field 'selection__myfield'
        """
        real_fields = fields
        if fields:
            # We remove fields which are not in _fields
            real_fields = [x for x in fields if x in self._fields]
        result = super().read(real_fields, load=load)
        # adding fields to result
        [result[0].update({x: False}) for x in fields if x not in real_fields]
        return result

    def button_apply(self):
        self.ensure_one()
