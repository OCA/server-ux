# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from lxml import etree
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestSearchCustom(TransactionCase):

    def setUp(self):
        super(TestSearchCustom, self).setUp()
        self.field = self.env.ref(
            'base_search_custom_field_filter.custom_field_filter_demo')
        self.customer_action = self.env.ref('base.action_partner_form')
        self.partner_kanban_view = self.env.ref("base.res_partner_kanban_view")
        self.partner_search_view = self.env.ref('base.view_res_partner_filter')

    def test_load_views(self):
        """
        Simulate the frontend default call for views
        :return:
        """
        views = self.env['res.partner'].load_views(self.customer_action.views)
        for view, values in views['fields_views'].iteritems():
            self.assertIn(
                'ir_ui_custom_filter_{}'.format(self.field.id),
                values['fields'],
            )

    def test_load_search(self):
        """
        Check if the created field is in search view
        :return:
        """
        res = self.env['res.partner'].fields_view_get(
            self.partner_search_view.id, 'search')
        arch = etree.fromstring(res['arch'])
        path = '//field[@name={}]'.format(
            "'ir_ui_custom_filter_%s'" % self.field.id,)
        field = arch.xpath(path)
        self.assertEquals(
            1,
            len(field)
        )

    def test_field_name(self):
        """
        Check the expression contraint
        :return:
        """
        vals = {
            'model_id': self.env.ref('base.model_res_partner').id,
            'name': 'Fake One',
            'expression': 'fake_field',
        }
        with self.assertRaises(ValidationError):
            self.env['ir.ui.custom.field.filter'].create(vals)
