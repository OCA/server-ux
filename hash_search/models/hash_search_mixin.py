# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.osv.orm import setup_modifiers
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from lxml import etree
import json


class HashSearchMixin(models.AbstractModel):
    _name = 'hash.search.mixin'

    hash_search_ids = fields.One2many(
        'hash.search',
        compute='_compute_hash_search'
    )

    @api.depends()
    def _compute_hash_search(self):
        for record in self:
            record.hash_search_ids = record.get_hash_search()

    def _hash_values(self):
        return {
            'object_id': '%s,%s' % (self._name, self.id)
        }

    @api.multi
    def get_hash_search(self):
        self.ensure_one()
        hash = self.env['hash.search'].search([
            ('res_id', '=', self.id),
            ('model', '=', self._name),
        ], limit=1)
        if not hash:
            return self.env['hash.search'].create(self._hash_values())
        return hash

    @api.model
    def _get_label_action(self):
        """
        We must define how the label ZPL2 action
        """
        raise UserError(_('Label action not defined'))

    def _get_printer(self):
        """
        We could rewrite the printer method. Usually an installation
        configuration
        """
        if self.env.user.printing_printer_id:
            return self.env.user.printing_printer_id
        raise UserError(_('Printer function not defined'))

    @api.multi
    def action_print_hash_label(self):
        self.ensure_one()
        label_action = self._get_label_action()
        content = label_action.render_label(self)
        self._get_printer().print_document(
            report=self.env['ir.actions.report'],
            content=content, doc_format='txt'
        )
        return True

    @api.model
    def _get_hash_button_attrs(self):
        return {}

    @api.model
    def _get_hash_button_string(self):
        return 'Print Hash Label'

    @api.model
    def _get_hash_button_icon(self):
        return 'fa-print'

    @api.model
    def _get_hash_button(self):
        return etree.Element(
            'button', attrib={
                'name': 'action_print_hash_label',
                'type': 'object',
                'class': 'oe_stat_button',
                'attrs': json.dumps(self._get_hash_button_attrs()),
                'string': self._get_hash_button_string(),
                'icon': self._get_hash_button_icon()
            }
        )

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            nodes = doc.xpath("//div[@name='button_box']")
            if nodes:
                node = nodes[0]
            else:
                sheet = doc.xpath('//sheet')
                if sheet:
                    node = etree.Element(
                        'div',
                        attrib={
                            'name': 'button_box',
                            'class': 'oe_button_box'
                        }
                    )
                    sheet[0].insert(0, node)
                else:
                    node = None
            if node is not None:
                button = self._get_hash_button()
                setup_modifiers(button)
                node.append(button)
            res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
