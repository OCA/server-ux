# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree
from odoo.tests import common


class TestHideFieldsBase(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")

    def _get_field_name_attrs(self, field_name, company, model, view_id):
        xml = etree.fromstring(
            self.env[model].sudo().with_context(
                company_id=company.id
            ).fields_view_get(
                view_id=view_id
            )['arch'].encode('utf-8')
        )
        return xml.xpath('//field[@name="%s"]' % field_name)[0].get('attrs')
