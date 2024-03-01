from odoo.exceptions import AccessError
from odoo.tests import SavepointCase
from odoo.tools import mute_logger


@mute_logger("odoo.addons.base.models.ir_rule")
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
        cls.user_admin = cls.env.ref("base.user_admin")

    def test_rule_standard_behaviour(self):
        """
        Test that standard behaviour is not influenced
        """
        self.user_admin.groups_id -= self.group_private_addresses
        self.partner_azure.read()
        with self.assertRaises(AccessError):
            self.private_address.with_user(self.user_admin).read()

        self.user_admin.groups_id += self.group_private_addresses
        self.partner_azure.read()
        self.private_address.with_user(self.user_admin).read()

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
        self.user_admin.groups_id -= self.group_private_addresses
        self.partner_azure.read()
        with self.assertRaises(AccessError):
            self.private_address.with_user(self.user_admin).read()

        self.user_admin.groups_id += self.group_private_addresses
        self.partner_azure.read()
        with self.assertRaises(AccessError):
            self.private_address.with_user(self.user_admin).read()

        self.partner_azure.name = "Some other name"
        with self.assertRaises(AccessError):
            self.partner_azure.with_user(self.user_admin).read()

        rule.active = False

        self.partner_azure.with_user(self.user_admin).read()
        self.private_address.with_user(self.user_admin).read()
