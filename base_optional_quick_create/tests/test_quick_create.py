# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestQuickCreate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.partner_model = cls.env["ir.model"].search([("model", "=", "res.partner")])

    def tearDown(self):
        super().tearDown()
        self.partner_model.avoid_quick_create = False

    def test_quick_create(self):
        partner = self.env["res.partner"].name_create("TEST partner")
        self.assertEqual(bool(partner), True)

        # Setting the flag, patches the method
        self.partner_model.avoid_quick_create = True
        with self.assertRaises(UserError):
            self.env["res.partner"].name_create("TEST partner")

        # Unsetting the flag, unpatches the method
        self.partner_model.avoid_quick_create = False
        partner = self.env["res.partner"].name_create("TEST partner")
        self.assertEqual(bool(partner), True)

        # New Model
        # Setting the flag, patches the method
        self.env["ir.model"].create(
            {"name": "Test Model", "model": "x_.test.model", "avoid_quick_create": True}
        )
        with self.assertRaises(UserError):
            self.env["x_.test.model"].name_create("TEST Model")

        # Unsetting the flag, unpatches the method
        self.env["ir.model"].create(
            {
                "name": "Test Model",
                "model": "x_.test.model.quick",
                "avoid_quick_create": False,
            }
        )
        test_quick = self.env["x_.test.model.quick"].name_create("TEST Model")
        self.assertEqual(bool(test_quick), True)

    def test_allow_quick_create(self):
        # Setting the flag, patches the method
        self.partner_model.avoid_quick_create = True
        with self.assertRaises(UserError):
            self.env["res.partner"].name_create("TEST allow_quick_create")

        # With allow_quick_create context flag
        partner = (
            self.env["res.partner"]
            .with_context(allow_quick_create=True)
            .name_create("TEST allow_quick_create")
        )
        self.assertEqual(bool(partner), True)

        # New Model
        # Setting the flag, patches the method
        self.env["ir.model"].create(
            {
                "name": "Test Model",
                "model": "x_.test.model.allow",
                "avoid_quick_create": True,
            }
        )
        # With allow_quick_create context flag
        test_allow = (
            self.env["x_.test.model.allow"]
            .with_context(allow_quick_create=True)
            .name_create("TEST Model")
        )
        self.assertEqual(bool(test_allow), True)
