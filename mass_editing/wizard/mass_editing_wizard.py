# -*- coding: utf-8 -*-
# © 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json
from lxml import etree

from odoo import tools
from odoo import api, models


class MassEditingWizard(models.TransientModel):
    _name = 'mass.editing.wizard'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        result = \
            super(MassEditingWizard, self).fields_view_get(
                view_id=view_id,
                view_type=view_type,
                toolbar=toolbar,
                submenu=submenu)
        context = self._context
        if context.get('mass_editing_object'):
            mass_obj = self.env['mass.object']
            editing_data = mass_obj.browse(context.get('mass_editing_object'))
            all_fields = {}
            xml_form = etree.Element('form', {
                'string': tools.ustr(editing_data.name)
            })
            xml_group = etree.SubElement(xml_form, 'group', {
                'colspan': '4',
                'col': '4',
            })
            model_obj = self.env[context.get('active_model')]
            field_info = model_obj.fields_get()
            for field in editing_data.field_ids:
                if field.ttype == "many2many":
                    all_fields[field.name] = field_info[field.name]
                    all_fields["selection__" + field.name] = {
                        'type': 'selection',
                        'string': field_info[field.name]['string'],
                        'selection': [('set', 'Set'),
                                      ('remove_m2m', 'Remove Specific'),
                                      ('remove_m2m_all', 'Remove All'),
                                      ('add', 'Add')]
                    }
                    etree.SubElement(xml_group, 'separator', {
                        'string': field_info[field.name]['string'],
                        'colspan': '4',
                    })
                    etree.SubElement(xml_group, 'field', {
                        'name': "selection__" + field.name,
                        'colspan': '4',
                        'nolabel': '1'
                    })
                    etree.SubElement(xml_group, 'field', {
                        'name': field.name,
                        'colspan': '4',
                        'nolabel': '1',
                        'attrs': "{'invisible': [('selection__" + 
                        field.name + "', '=', 'remove_m2m')]}",
                    })
                elif field.ttype == "one2many":
                    all_fields["selection__" + field.name] = {
                        'type': 'selection',
                        'string': field_info[field.name]['string'],
                        'selection': [('set', 'Set'),
                                      ('remove_o2m', 'Remove')],
                    }
                    all_fields[field.name] = {
                        'type': field.ttype,
                        'string': field.field_description,
                        'relation': field.relation,
                    }
                    etree.SubElement(xml_group, 'separator', {
                        'string': field_info[field.name]['string'],
                        'colspan': '4',
                    })
                    etree.SubElement(xml_group, 'field', {
                        'name': "selection__" + field.name,
                        'colspan': '4',
                        'nolabel': '1'
                    })
                    etree.SubElement(xml_group, 'field', {
                        'name': field.name,
                        'colspan': '4',
                        'nolabel': '1',
                        'attrs': "{'invisible':[('selection__" + 
                        field.name + "', '=', 'remove_o2m')]}",
                    })
                elif field.ttype == "many2one":
                    all_fields["selection__" + field.name] = {
                        'type': 'selection',
                        'string': field_info[field.name]['string'],
                        'selection': [('set', 'Set'), ('remove', 'Remove')],
                    }
                    all_fields[field.name] = {
                        'type': field.ttype,
                        'string': field.field_description,
                        'relation': field.relation,
                    }
                    etree.SubElement(xml_group, 'field', {
                        'name': "selection__" + field.name,
                    })
                    etree.SubElement(xml_group, 'field', {
                        'name': field.name,
                        'nolabel': '1',
                        'colspan': '2',
                        'attrs': "{'invisible':[('selection__" + 
                        field.name + "', '=', 'remove')]}",
                    })
                elif field.ttype == "float":
                    all_fields["selection__" + field.name] = {
                        'type': 'selection',
                        'string': field_info[field.name]['string'],
                        'selection': [('set', 'Set'),
                                      ('copy', 'Copy From'),
                                      ('val_add', '+'),
                                      ('val_sub', '-'),
                                      ('val_mul', '*'),
                                      ('val_div', '/'),
                                      ('remove', 'Remove')],
                    }
                    all_fields["set_selection_" + field.name] = {
                        'type': 'selection',
                        'string': 'Set calculation',
                        'selection': [('set_fix', 'Fixed'),
                                      ('set_per', 'Percentage')],
                    }
                    # Create Copy field
                    all_fields["selection__" + field.name + '_field_id'] = {
                        'type': 'many2one',
                        'string': 'Copy From',
                        'relation': 'ir.model.fields',
                    }
                    all_fields[field.name] = {
                        'type': field.ttype,
                        'string': field.field_description,
                        'relation': field.relation,
                    }
                    etree.SubElement(xml_group, 'field', {
                        'name': "selection__" + field.name,
                        'colspan': '2',
                    })
                    etree.SubElement(xml_group, 'field', {
                        'name': field.name,
                        'nolabel': '1',
                        'colspan': '1',
                        'attrs': "{'invisible': [('selection__" + 
                        field.name + "', 'in', ('remove', 'set')]}",
                    })
                    # Add Copy field in view
                    etree.SubElement(xml_group, 'field', {
                        'name': "selection__" + field.name + '_field_id',
                        'domain': "[('model_id.model', '=', '" + 
                        model_obj._name + "'), ('ttype', 'in', ['" + 
                        field.ttype + "', 'integer'])]",
                        'nolabel': '1',
                        'colspan': '1',
                        'placeholder': "Copy From...",
                    })
                    etree.SubElement(xml_group, 'label', {
                        'for': "",
                        'colspan': '1',
                        'attrs': "{'invisible': [('selection__" + 
                        field.name + "', 'in', ('remove', 'set', 'copy')]}",
                    })
                    etree.SubElement(xml_group, 'field', {
                        'name': "set_selection_" + field.name,
                        'nolabel': '1',
                        'colspan': '3',
                        'attrs': "{'invisible': [('selection__" + field.name + 
                        "', 'in', ('remove', 'set', 'copy')]}",
                    })
                elif field.ttype == "char":
                    all_fields["selection__" + field.name] = {
                        'type': 'selection',
                        'string': field_info[field.name]['string'],
                        'selection': [('set', 'Set'),
                                      ('remove', 'Remove'),
                                      ('copy', 'Copy From Another Field')],
                    }
                    # Create Copy field
                    all_fields["selection__" + field.name + '_field_id'] = {
                        'type': 'many2one',
                        'string': 'Copy From',
                        'relation': 'ir.model.fields',
                    }
                    all_fields[field.name] = {
                        'type': field.ttype,
                        'string': field.field_description,
                        'size': field.size or 256,
                    }
                    etree.SubElement(xml_group, 'field', {
                        'name': "selection__" + field.name,
                    })
                    # Add Copy field in view
                    etree.SubElement(xml_group, 'field', {
                        'name': field.name,
                        'nolabel': '1',
                        'attrs': "{'invisible':[('selection__" + 
                        field.name + "','=','remove')]}",
                    })
                    etree.SubElement(xml_group, 'field', {
                        'name': "selection__" + field.name + '_field_id',
                        'domain': "[('model_id.model', '=', '" + 
                        model_obj._name + "'), ('ttype', 'in', ['" + 
                        field.ttype + "', 'selection'])]",
                        'nolabel': '1',
                        'placeholder': "Copy From...",
                    })
                elif field.ttype == "integer":
                    all_fields["selection__" + field.name] = {
                        'type': 'selection',
                        'string': field_info[field.name]['string'],
                        'selection': [('set', 'Set'),
                                      ('remove', 'Remove'),
                                      ('copy', 'Copy From Another Field')],
                    }
                    # Create Copy field
                    all_fields["selection__" + field.name + '_field_id'] = {
                        'type': 'many2one',
                        'string': 'Copy From',
                        'relation': 'ir.model.fields',
                    }
                    all_fields[field.name] = {
                        'type': field.ttype,
                        'string': field.field_description,
                        'size': field.size or 256,
                    }
                    etree.SubElement(xml_group, 'field', {
                        'name': "selection__" + field.name,
                    })
                    # Add Copy field in view
                    etree.SubElement(xml_group, 'field', {
                        'name': field.name,
                        'nolabel': '1',
                        'attrs': "{'invisible':[('selection__" + 
                        field.name + "','=','remove')]}",
                    })
                    etree.SubElement(xml_group, 'field', {
                        'name': "selection__" + field.name + '_field_id',
                        'domain': "[('model_id.model', '=', '" + 
                        model_obj._name + "'), ('ttype', 'in', ['" + 
                        field.ttype + "', 'selection'])]",
                        'nolabel': '1',
                        'placeholder': "Copy From...",
                    })
                elif field.ttype == "boolean":
                    all_fields["selection__" + field.name] = {
                        'type': 'selection',
                        'string': field_info[field.name]['string'],
                        'selection': [('set', 'Set'),
                                      ('remove', 'Remove'),
                                      ('copy', 'Copy From Another Field')],
                    }
                    # Create Copy field
                    all_fields["selection__" + field.name + '_field_id'] = {
                        'type': 'many2one',
                        'string': 'Copy From',
                        'relation': 'ir.model.fields',
                    }
                    all_fields[field.name] = {
                        'type': field.ttype,
                        'string': field.field_description,
                        'size': field.size or 256,
                    }
                    etree.SubElement(xml_group, 'field', {
                        'name': "selection__" + field.name,
                    })
                    # Add Copy field in view
                    etree.SubElement(xml_group, 'field', {
                        'name': field.name,
                        'nolabel': '1',
                        'attrs': "{'invisible':[('selection__" + 
                        field.name + "','=','remove')]}",
                    })
                    etree.SubElement(xml_group, 'field', {
                        'name': "selection__" + field.name + '_field_id',
                        'domain': "[('model_id.model', '=', '" + 
                        model_obj._name + "'), ('ttype', 'in', ['" + 
                        field.ttype + "', 'selection'])]",
                        'nolabel': '1',
                        'placeholder': "Copy From...",
                    })
                elif field.ttype == 'selection':
                    all_fields["selection__" + field.name] = {
                        'type': 'selection',
                        'string': field_info[field.name]['string'],
                        'selection': [('set', 'Set'),
                                      ('remove', 'Remove')]
                    }
                    etree.SubElement(xml_group, 'field', {
                        'name': "selection__" + field.name,
                    })
                    etree.SubElement(xml_group, 'field', {
                        'name': field.name,
                        'nolabel': '1',
                        'colspan': '2',
                        'attrs': "{'invisible':[('selection__" + 
                        field.name + "', '=', 'remove')]}",
                    })
                    all_fields[field.name] = {
                        'type': field.ttype,
                        'string': field.field_description,
                        'selection': field_info[field.name]['selection'],
                    }
                else:
                    all_fields[field.name] = {
                        'type': field.ttype,
                        'string': field.field_description,
                    }
                    all_fields["selection__" + field.name] = {
                        'type': 'selection',
                        'string': field_info[field.name]['string'],
                        'selection': [('set', 'Set'), ('remove', 'Remove')]
                    }
                    if field.ttype == 'text':
                        etree.SubElement(xml_group, 'separator', {
                            'string': all_fields[field.name]['string'],
                            'colspan': '4',
                        })
                        etree.SubElement(xml_group, 'field', {
                            'name': "selection__" + field.name,
                            'colspan': '4',
                            'nolabel': '1',
                        })
                        etree.SubElement(xml_group, 'field', {
                            'name': field.name,
                            'colspan': '4',
                            'nolabel': '1',
                            'attrs': "{'invisible':[('selection__" + 
                            field.name + "','=','remove')]}",
                        })
                    else:
                        all_fields["selection__" + field.name] = {
                            'type': 'selection',
                            'string': field_info[field.name]['string'],
                            'selection': [('set', 'Set'),
                                          ('remove', 'Remove')]
                        }
                        etree.SubElement(xml_group, 'field', {
                            'name': "selection__" + field.name,
                        })
                        etree.SubElement(xml_group, 'field', {
                            'name': field.name,
                            'nolabel': '1',
                            'attrs': "{'invisible':[('selection__" + 
                            field.name + "','=','remove')]}",
                            'colspan': '2',
                        })
            # Patch fields with required extra data
            for field in all_fields.values():
                field.setdefault("views", {})
            etree.SubElement(xml_form, 'separator', {
                'string': '',
                'colspan': '3',
                'col': '3',
            })
            xml_group3 = etree.SubElement(xml_form, 'footer', {})
            etree.SubElement(xml_group3, 'button', {
                'string': 'Apply',
                'class': 'btn-primary',
                'type': 'object',
                'name': 'action_apply',
            })
            etree.SubElement(xml_group3, 'button', {
                'string': 'Close',
                'class': 'btn-default',
                'special': 'cancel',
            })
            root = xml_form.getroottree()
            result['arch'] = etree.tostring(root)
            result['fields'] = all_fields
            doc = etree.XML(result['arch'])
            for field in editing_data.field_ids:
                for node in doc.xpath(
                    "//field[@name='set_selection_" + field.name + "']"
                ):
                    modifiers = json.loads(node.get("modifiers", '{}'))
                    modifiers.update({'invisible': [(
                        "selection__" + field.name, 'not in',
                        ('val_add', 'val_sub', 'val_mul', 'val_div'))],
                        'required': [("selection__" + field.name, 'in',
                                      ('val_add', 'val_sub', 'val_mul',
                                       'val_div'))]}
                    )
                    node.set("modifiers", json.dumps(modifiers))
                field_name = "selection__" + field.name
                for node in doc.xpath("//field[@name='" + field.name + "']"):
                    modifiers = json.loads(node.get("modifiers", '{}'))
                    domain = [(field_name, '=', 'remove')]
                    if field.ttype == "many2many":
                        domain = [(field_name, '=', 'remove_m2m_all')]
                    elif field.ttype == "one2many":
                        domain = [(field_name, '=', 'remove_o2m')]
                    elif field.ttype in ['char', 'float', 'integer',
                                         'boolean']:
                        domain = [(field_name, 'in', ['remove', 'copy'])]
                    modifiers.update({'invisible': domain})
                    node.set("modifiers", json.dumps(modifiers))

                copy_field = "selection__" + field.name + "_field_id"
                for node in doc.xpath("//field[@name='" + copy_field + "']"):
                    modifiers = json.loads(node.get("modifiers", '{}'))
                    modifiers.update({
                        'invisible': [(field_name, '!=', 'copy')],
                        'required': [(field_name, '=', 'copy')],
                    })
                    node.set("modifiers", json.dumps(modifiers))

            result['arch'] = etree.tostring(doc)
        return result

    @api.model
    def create(self, vals):
        if (self._context.get('active_model') and
                self._context.get('active_ids')):
            fields_obj = self.env['ir.model.fields']
            model_obj = self.env[self._context.get('active_model')]
            model_field_obj = self.env['ir.model.fields']
            translation_obj = self.env['ir.translation']
            model_rec = model_obj.browse(self._context.get('active_ids'))
            model_id = self.env['ir.model'].search([
                ('model', '=', self._context.get('active_model'))])

            values = {}
            for key, val in vals.items():
                if key.startswith('selection_'):
                    split_key = key.split('__', 1)[1]
                    set_val = vals.get('set_selection_' + split_key)
                    if val == 'set':
                        values.update({split_key: vals.get(split_key, False)})
                    elif val == 'remove':
                        values.update({split_key: False})

                        # If field to remove is translatable,
                        # its translations have to be removed
                        model_field = model_field_obj.search([
                            ('model', '=', self._context.get('active_model')),
                            ('name', '=', split_key)])
                        if model_field and model_field.translate:
                            translation_ids = translation_obj.search([
                                ('res_id', 'in', self._context.get(
                                    'active_ids')),
                                ('type', '=', 'model'),
                                ('name', '=', u"{0},{1}".format(
                                    self._context.get('active_model'),
                                    split_key))])
                            translation_ids.unlink()

                    elif val in ['remove_m2m', 'remove_m2m_all']:
                        m2m_list = []
                        if vals.get(split_key):
                            for m2m_id in vals.get(split_key)[0][2]:
                                m2m_list.append((3, m2m_id))
                        if m2m_list:
                            values.update({split_key: m2m_list})
                        else:
                            values.update({split_key: [(5, 0, [])]})
                    elif val == 'remove_o2m':
                        # model_fieds will return the particular model
                        # in order to get the field of the model
                        # and its relation.
                        model_fields = self.env['ir.model.fields'].search(
                            [('name', '=', split_key),
                             ('model_id', '=', model_id and model_id.id)])
                        # field_model is relation of Object Relation
                        field_model = tools.ustr(model_fields and
                                                 model_fields.relation)
                        # field relation is relation field of O2m
                        field_relation = tools.ustr(
                            model_fields and
                            model_fields.relation_field)
                        # remove_ids is return O2m field particular ids
                        remove_ids = self.env[field_model].search(
                            [(field_relation, 'in',
                              self._context.get('active_ids'))])
                        o2m_list = [(2, rmv_id.id) for rmv_id in remove_ids]
                        values.update({split_key: o2m_list})
                    elif val == 'add':
                        if vals.get(split_key, False):
                            m2m_list = []
                            for m2m_id in vals.get(split_key, False)[0][2]:
                                m2m_list.append((4, m2m_id))
                            values.update({split_key: m2m_list})
                    elif val == 'copy':
                        field_id = vals.get(
                            'selection__' + split_key + '_field_id'
                        )
                        if field_id:
                            field_name = fields_obj.browse(field_id).name
                            for data in model_rec:
                                data.write({split_key: data[field_name]})

                    # Mathematical operations
                    elif val in ['val_add', 'val_sub', 'val_mul', 'val_div']:
                        split_val = vals.get(split_key, 0.0)
                        for data in model_rec:
                            split_key_data = data[split_key]
                            tot_val = 0
                            # Addition
                            if val == 'val_add':
                                if set_val == 'set_fix':
                                    tot_val = split_key_data + split_val
                                elif set_val == 'set_per':
                                    tot_val = split_key_data + \
                                        (split_key_data * split_val) / 100.0
                            # Subtraction
                            elif val == 'val_sub':
                                if set_val == 'set_fix':
                                    tot_val = split_key_data - split_val
                                elif set_val == 'set_per':
                                    tot_val = split_key_data - \
                                        (split_key_data * split_val) / 100.0
                            # Multiplication
                            elif val == 'val_mul':
                                if set_val == 'set_fix':
                                    tot_val = split_key_data * split_val
                                elif set_val == 'set_per':
                                    tot_val = split_key_data * \
                                        (split_key_data * split_val) / 100
                            # Division
                            elif val == 'val_div':
                                if set_val == 'set_fix':
                                    tot_val = split_key_data / split_val
                                elif set_val == 'set_per':
                                    tot_val = split_key_data / \
                                        (split_key_data * split_val) / 100
                            data.write({split_key: tot_val})
            if values:
                model_rec.write(values)
        return super(MassEditingWizard, self).create(vals)

    @api.multi
    def action_apply(self):
        return {'type': 'ir.actions.act_window_close'}

    def read(self, fields, load='_classic_read'):
        """ Without this call, dynamic fields build by fields_view_get()
            generate a log warning, i.e.:
            odoo.models:mass.editing.wizard.read() with unknown field 'myfield'
            odoo.models:mass.editing.wizard.read()
                with unknown field 'selection__myfield'
        """
        real_fields = fields
        if fields:
            # We remove fields which are not in _fields
            real_fields = [x for x in fields if x in self._fields]
        result = super(MassEditingWizard, self).read(real_fields, load=load)
        # adding fields to result
        [result[0].update({x: False}) for x in fields if x not in real_fields]
        return result
