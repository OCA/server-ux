# Copyright 2018 Creu Blanca
# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.tests.common import TransactionCase


class TestPartnerFind(TransactionCase):

    def test_partner(self):
        partner_obj = self.env['res.partner']
        ref = 'testing_partner_internal_reference'
        partner = partner_obj.create({
            'name': 'Testing partner',
            'ref': ref,
        })
        # We should find the partner when the ref is found
        self.assertEqual(
            partner.id,
            partner_obj.find_res_partner_by_ref_using_barcode(ref).get(
                'res_id', False))
        # No partner is found, then there is no res_id on the result
        self.assertFalse(
            partner_obj.find_res_partner_by_ref_using_barcode(
                '%s-%s' % (ref, ref)).get('res_id', False))
