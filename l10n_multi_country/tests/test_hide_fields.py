# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_test_helper import FakeModelLoader
from odoo.addons.l10n_multi_country.tests.test_base import TestHideFieldsBase


class TestHideFields(TestHideFieldsBase, FakeModelLoader):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .models import L10nMultiCountryDemo, ResCompany
        cls.loader.update_registry(
            (L10nMultiCountryDemo, ResCompany)
        )

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super(TestHideFields, cls).tearDownClass()

    def test_apply_attrs_custom_field(self):
        view = self.env['ir.ui.view'].create({
            'name': "test",
            'type': "form",
            'model': 'l10n_multi_country.demo',
            'arch': """
                <data>
                    <field name="name" />
                    <field name="custom_us_field" />
                </data>
            """
        })
        self.assertTrue(
            "'invisible': [('company_country_code','!=', 'US')]}" in
            self._get_field_name_attrs(
                'custom_us_field', self.company, 'l10n_multi_country.demo', view.id
            )
        )

    def test_apply_attrs_custom_field_exist(self):
        view = self.env['ir.ui.view'].create({
            'name': "test",
            'type': "form",
            'model': 'res.company',
            'arch': """
                <data>
                    <field name="name" />
                    <field name="company_country_code" invisible="1" />
                    <field name="custom_us_field" />
                </data>
            """
        })
        self.assertTrue(
            "'invisible': [('company_country_code','!=', 'US')]}" in
            self._get_field_name_attrs(
                'custom_us_field', self.company, 'res.company', view.id
            )
        )
