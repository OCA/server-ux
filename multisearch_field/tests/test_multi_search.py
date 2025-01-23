# Copyright 2024 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestMultisearch(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner_1 = self.env["res.partner"].create(
            {
                "name": "partner_one",
            }
        )
        self.partner_2 = self.env["res.partner"].create(
            {
                "name": "partner_two",
            }
        )
        self.partner_3 = self.env["res.partner"].create(
            {
                "name": "partner_three",
            }
        )

    def test_multi_search(self):
        search_1 = self.env["res.partner"].search(
            [("name", "like", "/partner_one|partner_two")]
        )
        self.assertEqual(
            search_1,
            self.env["res.partner"].browse((self.partner_1.id, self.partner_2.id)),
        )
        search_2 = self.env["res.partner"].search([("name", "ilike", "/one;two|four")])
        self.assertEqual(
            search_2,
            self.env["res.partner"].browse((self.partner_1.id, self.partner_2.id)),
        )
        search_3 = self.env["res.partner"].search([("name", "ilike", "/one;two|three")])
        self.assertEqual(
            search_3,
            self.env["res.partner"].browse(
                (self.partner_1.id, self.partner_2.id, self.partner_3.id)
            ),
        )
        search_4 = self.env["res.partner"].search([("name", "ilike", "one;two|three")])
        self.assertEqual(
            search_4,
            self.env["res.partner"],
        )
