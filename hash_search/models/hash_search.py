# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from ast import literal_eval
import base64
import json


class HashSearch(models.Model):
    _name = 'hash.search'
    _description = 'Hash Search'

    @api.model
    def hash_search_models(self):
        """
        The different affected models have to be attached here in order to
        use the information in other modules
        """
        return []

    object_id = fields.Reference(
        selection=hash_search_models,
        required=True,
    )
    model = fields.Char(compute='_compute_object', store=True)
    res_id = fields.Integer(compute='_compute_object', store=True)
    name = fields.Char(required=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         'name must be unique'),
        ('object_id_unique', 'unique(object_id)',
         'object_id must be unique'),
    ]

    @api.multi
    def check_access_rule(self, operation):
        return self.object_id.check_access_rule(operation)

    @api.depends('object_id')
    def _compute_object(self):
        for record in self:
            record.res_id = record.object_id.id
            record.model = record.object_id._name

    @api.model
    def get_hash_name(self, vals):
        return base64.b64encode(
            vals['object_id'].encode('utf-8')).decode('utf-8')

    @api.model
    def create(self, vals):
        if not vals.get('name', False):
            vals['name'] = self.get_hash_name(vals)
        return super().create(vals)

    @api.multi
    def find_hash(self, barcode):
        hash = self.search([('name', '=', barcode)], limit=1)
        if not hash:
            action = self.env.ref('hash_search.find_hash')
            result = action.read()[0]
            context = literal_eval(result['context'])
            context.update({
                'default_state': 'warning',
                'default_status': _('Document cannot be found')
            })
            result['context'] = json.dumps(context)
            return result
        res = self.env[hash.model].browse(hash.res_id)
        res.check_access_rights('read')

        result = {
            "type": "ir.actions.act_window",
            "res_model": hash.model,
            "views": [[res.get_formview_id(), "form"]],
            "res_id": hash.res_id,
            "target": "main",
        }
        return result
