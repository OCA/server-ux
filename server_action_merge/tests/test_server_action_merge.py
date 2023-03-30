# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import exceptions
from odoo.tests.common import TransactionCase


class TestServerActionMerge(TransactionCase):
    def setUp(self):
        super().setUp()
        self.user_demo = self.env.ref("base.user_demo")
        self.user_demo.phone = False
        self.user_test = self.env["res.users"].create(
            {"login": "testuser", "name": "testuser", "phone": "from testuser"}
        )
        self.partner_test = self.user_test.partner_id

    def _get_wizard(self, records, merge_action):
        wizard_action = merge_action.with_context(
            active_model=records._name,
            active_id=records[:1].id,
            active_ids=records.ids,
        ).run()
        return self.env[wizard_action["res_model"]].browse(wizard_action["res_id"])

    def test_user_merge(self):
        """Test we can merge users"""
        wizard = self._get_wizard(
            self.user_test + self.env.ref("base.user_demo"),
            self.env.ref("server_action_merge.server_action_merge_users"),
        )
        self.assertEqual(wizard.target_line_id.record, self.user_demo)
        self.assertEqual(wizard.target_line_xmlid, "base.user_demo")
        self.assertEqual(wizard.xmlid_count, 1)
        wizard.action_id.groups_id = self.env.ref("base.group_portal")
        with self.assertRaises(exceptions.AccessError):
            wizard.action_merge()
        wizard.action_id.groups_id = False
        wizard.action_merge()
        self.assertEqual(self.user_demo.phone, "from testuser")
        self.assertFalse(self.user_test.exists())
        self.assertFalse(self.partner_test.exists())

    def test_user_merge_deactivate(self):
        action = self.env.ref("server_action_merge.server_action_merge_users")
        action.merge_handling = "deactivate"
        wizard = self._get_wizard(
            self.user_test + self.env.ref("base.user_demo"),
            self.env.ref("server_action_merge.server_action_merge_users"),
        )
        wizard.action_merge()
        self.assertTrue(self.user_test.exists())
        self.assertFalse(self.user_test.active)
