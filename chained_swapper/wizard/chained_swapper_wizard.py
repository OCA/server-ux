# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo.tools.safe_eval import safe_eval
from odoo import _, api, models
from odoo.exceptions import UserError


class ChainedSwapperWizard(models.TransientModel):
    _name = 'chained.swapper.wizard'
    _description = "Wizard chained swapper"

    @api.model
    def default_get(self, fields):
        context = self.env.context
        if context.get('chained_swapper_id'):
            records = self.env[context.get('active_model')].browse(
                context.get('active_ids'))
            chained_swapper = self.env['chained.swapper'].browse(
                context.get('chained_swapper_id'))
            for constraint in chained_swapper.constraint_ids:
                if safe_eval(constraint.expression, {'records': records}):
                    raise UserError(_(
                        "Not possible to swap the field due to the constraint"
                    ) + ": " + constraint.name)
        return super().default_get(fields)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        """ As we don't have any field in this model, result['fields']
        and result['arch'] are modified to add dynamically the
        corresponding field.
        """
        res = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        if not self.env.context.get('chained_swapper_id'):
            return res
        chained_swapper = self.env['chained.swapper'].browse(
            self.env.context.get('chained_swapper_id'))
        model_obj = self.env[self.env.context.get('active_model')]
        field_info = model_obj.fields_get()
        field = chained_swapper.field_id
        # Fields dict
        all_fields = {
            field.name: {
                'type': field.ttype,
                'string': field.field_description,
                "views": {},
            }
        }
        if field.ttype in ["many2many", "many2one"]:
            all_fields[field.name]['relation'] = field.relation
        elif field.ttype == 'selection':
            field_selection = field_info[field.name]['selection']
            all_fields[field.name]['selection'] = field_selection
        # XML view definition
        doc = etree.XML(res['arch'])
        group_node = doc.xpath("//group[@name='swap_field_group']")[0]
        etree.SubElement(
            group_node, 'field', {'name': field.name, 'colspan': '4'})
        if field.ttype in ["one2many", "many2many", "text"]:
            group_node.set('string', field.field_description)
            group_node.set('nolabel', '1')
        res.update(
            arch=etree.tostring(doc, encoding='unicode'), fields=all_fields)
        return res

    @api.model
    def create(self, vals):
        """ As we don't have any field in this model, the key-value pair
        received in vals dict are only used to change the value in the active
        models.
        """
        model_obj = self.env[self.env.context.get('active_model')]
        context = self.env.context
        field_name, new_value = list(vals.items())[0]
        # write the active model
        model = model_obj.browse(self.env.context.get('active_ids'))
        original_values = {m.id: m[field_name] for m in model}
        model.write(vals)
        if hasattr(model, 'message_post'):
            self.post_chained_swap(
                model, field_name, original_values, new_value)
        # write chained models
        chained_swapper_obj = self.env['chained.swapper']
        chained_swapper = chained_swapper_obj.browse(
            context.get('chained_swapper_id'))
        for sub_field in chained_swapper.sub_field_ids:
            chain_fields = sub_field.sub_field_chain.split('.')
            field_name = chain_fields.pop()
            chain_model = model
            for chain_field in chain_fields:
                chain_model = chain_model.mapped(chain_field)
            original_values = {cm.id: cm[field_name] for cm in chain_model}
            chain_model.write({field_name: new_value})
            # post swap
            if hasattr(chain_model, 'message_post'):
                self.post_chained_swap(
                    chain_model, field_name, original_values, new_value)
        return super().create({})

    @api.multi
    def change_action(self):
        return {'type': 'ir.actions.act_window_close'}

    @api.model
    def post_chained_swap(self, model, field_name, original_values, new_value):
        def human_readable_field(value):
            result = value
            field_def = model._fields[field_name]
            if field_def.type == "selection":
                if type(field_def.selection) == list:
                    selection = field_def.selection
                else:
                    selection = field_def.selection(self)
                for selection_item in selection:
                    if selection_item[0] == value:
                        result = selection_item[1]
                        break
            elif field_def.type == "many2one":
                if type(value) == int:
                    result = self.env[field_def.comodel_name].browse(value)
                result = result.display_name
            elif field_def.type == "many2many":
                if type(value) == list:
                    ids = value[0][2]
                    value = self.env[field_def.comodel_name].browse(ids)
                result = str(value.mapped('display_name'))
            return result
        field_desc = model._fields[field_name].string
        new_value = human_readable_field(new_value)
        for m in model:
            original_value = human_readable_field(original_values[m.id])
            m.message_post(
                body=_("<b>Chained swap done</b>:") + "<br/>%s: %s ⇒ %s" % (
                    field_desc, original_value, new_value)
            )

    def read(self, fields, load='_classic_read'):
        """Without this call, dynamic fields build by fields_view_get()
        generate a crash and warning, i.e.: read() with unknown field 'myfield'
        """
        real_fields = set(fields) & set(self._fields)
        result = super().read(list(real_fields), load=load)
        result[0].update({x: False for x in set(fields) - real_fields})
        return result
