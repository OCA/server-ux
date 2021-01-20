# Copyright 2021 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from lxml import etree
from odoo import api, models, fields
import logging
_logger = logging.getLogger(__name__)


class L10nMultiCountryMixin(models.AbstractModel):
    _name = 'l10n_multi_country.mixin'
    _description = 'l10n_multi_country Mixin'

    company_country_code = fields.Char(
        string="Company country code",
        compute="_compute_company_country_code",
        store=False,
        readonly=True
    )

    def _compute_company_country_code(self):
        for item in self:
            company = self.env.user.company_id
            if ("company_id" in self.fields_get_keys() and self.company_id):
                company = self.company_id
            if self._name == 'res.company':
                company = self
            item.company_country_code = company.country_id.code

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        result = super(L10nMultiCountryMixin, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu
        )
        doc = etree.XML(result['arch'])
        if not doc.xpath('//field[@name="company_country_code"]'):
            elem = etree.Element(
                'field', {
                    'name': 'company_country_code',
                    'invisible': '1'
                })
            doc.xpath("//field")[0].addprevious(elem)
        for field_get in doc.xpath("//field"):
            try:
                field = self._fields[field_get.attrib['name']]
                if hasattr(field, 'country'):
                    field_get.set(
                        'attrs',
                        "{'invisible': [('company_country_code','!=', '%s')]}" %
                        field.country.upper()
                    )
            except:
                _logger.info('Skip %s' % field_get.attrib['name'])
        arch, fields = self.env['ir.ui.view'].postprocess_and_fields(
            self._name, doc, view_id,
        )
        result.update(arch=arch, fields=fields)
        return result
