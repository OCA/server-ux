# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import Form, TransactionCase


class TestBaseTechnicalFeatures(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Group references
        cls.group_no_one = cls.env.ref("base.group_no_one")
        cls.group_technical_features_xmlid = (
            "base_technical_features.group_technical_features"
        )
        cls.group_technical_features = cls.env.ref(cls.group_technical_features_xmlid)
        # Create a test view for the hidden fields
        cls.view = cls.env["ir.ui.view"].create(
            {
                "name": "Test view",
                "model": "res.users",
                "type": "form",
                "arch": """
                    <form>
                        <field name="name" />
                        <field name="partner_id" groups="base.group_no_one" />
                    </form>
                """,
            }
        )
        # Create a test technical menu
        action = cls.env["ir.actions.act_window"].create(
            {
                "name": "action (test)",
                "res_model": "res.partner",
                "view_ids": [Command.create({"view_mode": "form"})],
            }
        )
        cls.menu = cls.env["ir.ui.menu"].create(
            {
                "name": "child menu (test)",
                "action": f"{action._name},{action.id}",
                "group_ids": [Command.set(cls.group_no_one.ids)],
            }
        )

    def test_technical_features_field(self):
        self.assertFalse(self.env.user.technical_features)
        self.assertFalse(self.env.user.has_group(self.group_technical_features_xmlid))
        # Setting the field must add the group to the user
        self.env.user.technical_features = True
        self.assertTrue(self.env.user.has_group(self.group_technical_features_xmlid))
        # Setting the field to False must remove the group from the user
        self.env.user.technical_features = False
        self.assertFalse(self.env.user.has_group(self.group_technical_features_xmlid))
        # Adding the group must also be reflected in the field
        self.env.user.group_ids += self.group_technical_features
        self.assertTrue(self.env.user.technical_features)
        # Removing the group must also be reflected in the field
        self.env.user.group_ids -= self.group_technical_features
        self.assertFalse(self.env.user.technical_features)

    def test_visible_menu_hidden(self):
        """The menu is not visible when technical features is not enabled"""
        self.assertNotIn(self.menu.id, self.env["ir.ui.menu"]._visible_menu_ids())

    def test_visible_menu_with_technical_features(self):
        """The menu is visible when technical features is enabled"""
        self.env.user.technical_features = True
        self.assertIn(self.menu.id, self.env["ir.ui.menu"]._visible_menu_ids())

    def test_visible_menu_with_debug_mode(self):
        """The menu is visible when debug mode is enabled

        This just tests we haven't broken the core behavior of the debug mode
        """
        self.assertFalse(self.env.user.technical_features)
        self.assertIn(
            self.menu.id, self.env["ir.ui.menu"]._visible_menu_ids(debug=True)
        )

    def test_visible_fields_hidden(self):
        """A technical field is hidden by default"""
        form = Form(self.env["res.users"], view=self.view)
        self.assertTrue(form._get_modifier("partner_id", "invisible"))

    def test_visible_fields_with_technical_features(self):
        """A technical field is visible when technical features is enabled"""
        self.env.user.technical_features = True
        form = Form(self.env["res.users"], view=self.view)
        self.assertFalse(form._get_modifier("partner_id", "invisible"))

    def test_visible_fields_with_debug_mode(self):
        """A technical field is visible when debug mode is enabled

        This just tests we haven't broken the core behavior of the debug mode
        """
        self.assertFalse(self.env.user.technical_features)
        with self.debug_mode():
            form = Form(self.env["res.users"], view=self.view)
            self.assertFalse(form._get_modifier("partner_id", "invisible"))

    def test_field_hidden_only_in_debug(self):
        """A technical field is hidden only in debug mode"""
        # The partner_id field is hidden in debug mode, so it must be hidden
        # when technical features are enabled
        self.view.arch = """
            <form>
                <field name="name" />
                <field name="partner_id" groups="!base.group_no_one" />
            </form>
        """
        self.env.user.technical_features = True
        form = Form(self.env["res.users"], view=self.view)
        self.assertTrue(form._get_modifier("partner_id", "invisible"))
