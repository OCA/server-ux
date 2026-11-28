# Copyright 2026 CIT Services
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase


class TestBaseAction(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        polluted_columns = [
            ("res_partner", "autopost_bills"),
            ("res_users", "notification_type"),
            ("res_users_settings", "calendar_default_privacy"),
        ]
        for table, column in polluted_columns:
            cls.env.cr.execute(
                f"""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name='{table}' AND column_name='{column}'
            """
            )
            if cls.env.cr.fetchone():
                cls.env.cr.execute(
                    f"ALTER TABLE {table} ALTER COLUMN {column} DROP NOT NULL"
                )

        cls.group_user = cls.env.ref("base.group_user")

        cls.child_group = cls.env["res.groups"].create(
            {
                "name": "User: Own Documents Only",
                "implied_ids": [Command.link(cls.group_user.id)],
            }
        )
        cls.parent_group = cls.env["res.groups"].create(
            {
                "name": "User: All Documents",
                "implied_ids": [Command.link(cls.child_group.id)],
            }
        )

        cls.unrelated_group = cls.env["res.groups"].create(
            {
                "name": "Project / User",
                "implied_ids": [Command.link(cls.group_user.id)],
            }
        )

        cls.test_user = cls.env["res.users"].create(
            {
                "name": "Test Action User",
                "login": "test_action_user",
                "groups_id": [Command.set([cls.env.ref("base.group_system").id])],
            }
        )

        cls.model_res_partner = cls.env["ir.model"].search(
            [("model", "=", "res.partner")], limit=1
        )

        cls.window_action = cls.env["ir.actions.act_window"].create(
            {
                "name": "Test Window Action",
                "res_model": "res.partner",
                "binding_model_id": cls.model_res_partner.id,
            }
        )

    def test_restricted_action_inheritance(self):
        """Test that restricting an action hides it from bindings."""
        self.child_group.write(
            {"restricted_window_action_ids": [Command.link(self.window_action.id)]}
        )
        self.test_user.write(
            {
                "groups_id": [
                    Command.set(
                        [self.parent_group.id, self.env.ref("base.group_system").id]
                    )
                ]
            }
        )
        with self.assertRaises(AccessError):
            self.window_action.with_user(self.test_user)._get_action_dict()

        bindings = (
            self.env["ir.actions.actions"]
            .with_user(self.test_user)
            .get_bindings("res.partner")
        )
        action_bindings = [a["id"] for a in bindings.get("action", [])]
        self.assertNotIn(self.window_action.id, action_bindings)

        self.child_group.write(
            {"restricted_window_action_ids": [Command.unlink(self.window_action.id)]}
        )
        self.parent_group.write(
            {"restricted_window_action_ids": [Command.link(self.window_action.id)]}
        )
        with self.assertRaises(AccessError):
            self.window_action.with_user(self.test_user)._get_action_dict()

        bindings = (
            self.env["ir.actions.actions"]
            .with_user(self.test_user)
            .get_bindings("res.partner")
        )
        action_bindings = [a["id"] for a in bindings.get("action", [])]
        self.assertNotIn(self.window_action.id, action_bindings)

        self.test_user.write(
            {
                "groups_id": [
                    Command.set(
                        [
                            self.child_group.id,
                            self.unrelated_group.id,
                            self.env.ref("base.group_system").id,
                        ]
                    )
                ]
            }
        )

        self.window_action.with_user(self.test_user)._get_action_dict()

        bindings = (
            self.env["ir.actions.actions"]
            .with_user(self.test_user)
            .get_bindings("res.partner")
        )
        action_bindings = [a["id"] for a in bindings.get("action", [])]
        self.assertIn(self.window_action.id, action_bindings)

    def test_superuser_bypass(self):
        """Superuser bypasses restrictions entirely."""
        self.child_group.write(
            {"restricted_window_action_ids": [Command.link(self.window_action.id)]}
        )
        root_user = self.env.ref("base.user_root") or self.env.user.browse(1)
        self.window_action.with_user(root_user)._check_action_action_restrictions()
        self.assertFalse(
            self.window_action.with_user(root_user)._is_action_action_restricted()
        )
        bindings = (
            self.env["ir.actions.actions"]
            .with_user(root_user)
            .get_bindings("res.partner")
        )
        action_bindings = [a["id"] for a in bindings.get("action", [])]
        self.assertIn(self.window_action.id, action_bindings)

    def test_no_group_overlap(self):
        """User has no group overlap with the restricted group."""
        self.child_group.write(
            {"restricted_window_action_ids": [Command.link(self.window_action.id)]}
        )
        self.test_user.write(
            {
                "groups_id": [
                    Command.set(
                        [
                            self.unrelated_group.id,
                            self.env.ref("base.group_system").id,
                        ]
                    )
                ]
            }
        )
        self.assertFalse(
            self.window_action.with_user(self.test_user)._is_action_action_restricted()
        )

    def test_get_bindings_filtering(self):
        """Test that get_bindings filters out restricted actions."""
        self.child_group.write(
            {"restricted_window_action_ids": [Command.link(self.window_action.id)]}
        )
        self.test_user.write(
            {
                "groups_id": [
                    Command.set(
                        [self.child_group.id, self.env.ref("base.group_system").id]
                    )
                ]
            }
        )

        import unittest.mock as mock

        mock_result = {"action": [{"id": self.window_action.id, "name": "Test Action"}]}
        with mock.patch(
            "odoo.addons.base.models.ir_actions.IrActions.get_bindings",
            return_value=mock_result,
        ):
            bindings = (
                self.env["ir.actions.actions"]
                .with_user(self.test_user)
                .get_bindings("res.partner")
            )
            self.assertNotIn("action", bindings)
