# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import ast
from datetime import date, datetime

from lxml import etree
from markupsafe import Markup

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class ChainedSwapperWizard(models.TransientModel):
    _name = "chained.swapper.wizard"
    _description = "Wizard chained swapper"

    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )

    @api.model
    def default_get(self, fields):
        context = self.env.context
        if context.get("chained_swapper_id"):
            records = self.env[context.get("active_model")].browse(
                context.get("active_ids")
            )
            exp_dict = {
                "records": records,
                "env": self.env,
                "date": date,
                "datetime": datetime,
            }
            chained_swapper = self.env["chained.swapper"].browse(
                context.get("chained_swapper_id")
            )
            for constraint in chained_swapper.constraint_ids:
                if safe_eval(constraint.expression, exp_dict):
                    raise UserError(
                        self.env._(
                            "Not possible to swap the field due to the constraint"
                        )
                        + ": "
                        + constraint.name
                    )
        return super().default_get(fields)

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        chained_swapper_id = self.env.context.get("chained_swapper_id")
        chained_swapper = self.env["chained.swapper"].browse(chained_swapper_id)
        res = super().fields_get(allfields, attributes)
        field = chained_swapper.field_id
        model = self.env[field.model]
        field_info = model.fields_get()
        res.update({field.name: field_info[field.name]})
        return res

    def onchange(self, values, field_names, fields_spec):
        fields_spec = {k: v for k, v in fields_spec.items() if k in self._fields}
        return super().onchange(values, field_names, fields_spec)

    @api.model
    def get_views(self, views, options=None):
        action = self.env["ir.actions.act_window"].browse(options.get("action_id"))
        context = ast.literal_eval(action.context)
        self = self.with_context(chained_swapper_id=context.get("chained_swapper_id"))
        res = super().get_views(views, options)
        return res

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        """As we don't have any field in this model, result['fields']
        and result['arch'] are modified to add dynamically the
        corresponding field.
        """
        action = self.env["ir.actions.act_window"].browse(options.get("action_id"))
        context = ast.literal_eval(action.context)
        chained_swapper = self.env["chained.swapper"].browse(
            context.get("chained_swapper_id")
        )
        self = self.with_context(chained_swapper_id=context.get("chained_swapper_id"))
        field = chained_swapper.field_id
        res = super().get_view(view_id, view_type, **options)
        # XML view definition
        doc = etree.XML(res["arch"])
        group_node = doc.xpath("//group[@name='swap_field_group']")[0]
        etree.SubElement(group_node, "field", {"name": field.name})
        if field.ttype in ["one2many", "many2many", "text"]:
            group_node.set("string", field.field_description)
            group_node.set("nolabel", "1")
        res.update(arch=etree.tostring(doc, encoding="unicode"))
        return res

    @api.model_create_multi
    def create(self, vals_list):
        """As we don't have any field in this model, the key-value pair
        received in vals dict are only used to change the value in the active
        models.
        """
        for vals in vals_list:
            model_obj = self.env[self.env.context.get("active_model")]
            context = self.env.context
            field_name, new_value = list(vals.items())[0]
            # write the active model
            model = model_obj.browse(self.env.context.get("active_ids"))
            original_values = {m.id: m[field_name] for m in model}
            model.write(vals)
            if hasattr(model, "message_post"):
                self.post_chained_swap(model, field_name, original_values, new_value)
            # write chained models
            chained_swapper_obj = self.env["chained.swapper"]
            chained_swapper = chained_swapper_obj.browse(
                context.get("chained_swapper_id")
            )
            for sub_field in chained_swapper.sub_field_ids:
                chain_fields = sub_field.sub_field_chain.split(".")
                field_name = chain_fields.pop()
                chain_model = model
                for chain_field in chain_fields:
                    chain_model = chain_model.mapped(chain_field)
                original_values = {cm.id: cm[field_name] for cm in chain_model}
                chain_model.write({field_name: new_value})
                # post swap
                if hasattr(chain_model, "message_post"):
                    self.post_chained_swap(
                        chain_model, field_name, original_values, new_value
                    )
        return super().create([{} for _ in vals_list])

    def change_action(self):
        return {"type": "ir.actions.act_window_close"}

    @api.model
    def post_chained_swap(self, model, field_name, original_values, new_value):
        def human_readable_field(value):
            result = value
            field_def = model._fields[field_name]
            if field_def.type == "selection":
                if type(field_def.selection) is list:
                    selection = field_def.selection
                else:
                    selection = field_def.selection(self)
                for selection_item in selection:
                    if selection_item[0] == value:
                        result = selection_item[1]
                        break
            elif field_def.type == "many2one":
                if type(value) is int:
                    result = self.env[field_def.comodel_name].browse(value)
                result = result.display_name
            elif field_def.type == "many2many":
                if type(value) is list:
                    ids = value[0][2]
                    value = self.env[field_def.comodel_name].browse(ids)
                result = str(value.mapped("display_name"))
            return result

        field_desc = model._fields[field_name].string
        new_value = human_readable_field(new_value)
        for m in model:
            original_value = human_readable_field(original_values[m.id])
            body = Markup(
                self.env._(
                    "<b>Chained swap done</b>:<br/>%(field)s: %(old)s ⇒ %(new)s",
                    field=field_desc,
                    old=original_value,
                    new=new_value,
                )
            )
            m.message_post(body=body)

    def read(self, fields, load="_classic_read"):
        """Without this call, dynamic fields build by get_view()
        generate a crash and warning, i.e.: read() with unknown field 'myfield'
        """
        real_fields = set(fields) & set(self._fields)
        result = super().read(list(real_fields), load=load)
        result[0].update({x: False for x in set(fields) - real_fields})
        return result
