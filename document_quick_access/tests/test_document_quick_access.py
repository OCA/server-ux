# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


@common.at_install(False)
@common.post_install(True)
class TestDocumentQuickAccess(TransactionCase):
    def setUp(self):
        super().setUp()
        self.model = 'res.partner'
        self.model_id = self.env.ref('base.model_res_partner')
        self.rule = self.env['document.quick.access.rule'].create({
            'model_id': self.model_id.id,
            'name': 'PARTNER',
            'priority': 1,
            'barcode_format': 'standard',
        })
        self.partner = self.env['res.partner'].create({
            'name': 'Partner test',
        })

    def test_generation(self):
        code = self.partner.get_quick_access_code()
        self.assertTrue(code)
        partner = self.env['document.quick.access.rule'].read_code(code)
        self.assertEqual(partner, self.partner)
        action = self.env['document.quick.access.rule'].read_code_action(code)
        self.assertEqual(action['res_model'], partner._name)
        self.assertEqual(action['res_id'], partner.id)

    def test_not_found(self):
        code = self.partner.get_quick_access_code()
        self.assertTrue(code)
        self.rule.toggle_active()
        with self.assertRaises(UserError):
            self.env['document.quick.access.rule'].read_code(code)
        action = self.env['document.quick.access.rule'].read_code_action(code)
        self.assertEqual(action['res_model'], 'barcode.action')

    def test_no_code(self):
        self.rule.toggle_active()
        self.assertFalse(self.partner.get_quick_access_code())

    def test_generation_b64(self):
        self.rule.barcode_format = 'b64_standard'
        self.test_generation()

    def test_not_found_b64(self):
        self.rule.barcode_format = 'b64_standard'
        self.test_not_found()
