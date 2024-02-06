from odoo.exceptions import AccessError
from odoo.tests import SavepointCase
from odoo.tools import mute_logger

from ..hooks import uninstall_hook


class TestBaseRuleOverride(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.rule_model = cls.env["ir.rule"]
        cls.partner_model = cls.env["res.partner"]
        cls.group_user = cls.env.ref("base.group_user")
        cls.partner_azure = cls.env.ref("base.res_partner_12")
        cls.private_address = cls.partner_model.create(
            {
                "name": "Private Test",
                "type": "private",
                "parent_id": cls.partner_azure.id,
            }
        )
        cls.rule_public_contacts = cls.env.ref("base.res_partner_rule_private_employee")
        cls.rule_private_contacts = cls.env.ref("base.res_partner_rule_private_group")
        cls.group_private_addresses = cls.env.ref("base.group_private_addresses")
        cls.user_demo = cls.env.ref("base.user_demo")

    @mute_logger("odoo.addons.base.models.ir_rule")
    def test_rule_standard_behaviour(self):
        """
        Test that standard behaviour is not influenced
        """
        self.assertNotIn(self.group_private_addresses, self.user_demo.groups_id)
        self.partner_azure.with_user(self.user_demo).read()
        with self.assertRaises(AccessError):
            self.private_address.with_user(self.user_demo).read()

        self.user_demo.groups_id += self.group_private_addresses
        self.partner_azure.with_user(self.user_demo).read()
        self.private_address.with_user(self.user_demo).read()

    @mute_logger("odoo.addons.base.models.ir_rule")
    def test_rule_override(self):
        """
        Test that an "override" rule denies access
        to a record even if other rules pass
        """
        rule = self.rule_model.create(
            {
                "name": "Test rule",
                "model_id": self.env.ref("base.model_res_partner").id,
                "groups": [(4, self.group_user.id)],
                "domain_force": """[("name", "ilike", "Azure")]""",
                "is_override": True,
            }
        )
        self.assertNotIn(self.group_private_addresses, self.user_demo.groups_id)
        self.partner_azure.with_user(self.user_demo).read()
        with self.assertRaises(AccessError):
            self.private_address.with_user(self.user_demo).read()

        self.user_demo.groups_id += self.group_private_addresses
        self.partner_azure.with_user(self.user_demo).read()
        with self.assertRaises(AccessError):
            self.private_address.with_user(self.user_demo).read()

        self.partner_azure.name = "Some other name"
        with self.assertRaises(AccessError):
            self.partner_azure.with_user(self.user_demo).read()

        rule.active = False

        self.partner_azure.with_user(self.user_demo).read()
        self.private_address.with_user(self.user_demo).read()

    @mute_logger("odoo.addons.base.models.ir_rule")
    def test_uninstall_hook(self):
        rule = self.rule_model.create(
            {
                "name": "Test rule",
                "model_id": self.env.ref("base.model_res_partner").id,
                "groups": [(4, self.group_user.id)],
                "domain_force": """[("name", "ilike", "Azure")]""",
                "is_override": True,
            }
        )
        rule_2 = rule.copy()
        all_rules = self.rule_model.search([("is_override", "=", True)])
        self.assertEqual(all_rules, rule + rule_2)

        uninstall_hook(self.env.cr, False)

        self.assertFalse(self.rule_model.search([("is_override", "=", True)]))
        self.assertFalse(rule.active)
        self.assertFalse(rule_2.active)
