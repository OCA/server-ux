# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import Command
from odoo.tests.common import TransactionCase


class TestViewActionVisibility(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_model = cls.env["ir.model"].search(
            [("model", "=", "res.partner")], limit=1
        )
        cls.test_group = cls.env["res.groups"].create(
            {"name": "Test Group for Action Visibility"}
        )
        base_user_group = cls.env.ref("base.group_user")
        cls.user_in_group = cls.env["res.users"].create(
            {
                "name": "User In Group",
                "login": "user_in_group",
                "groups_id": [Command.set([cls.test_group.id, base_user_group.id])],
            }
        )
        cls.user_not_in_group = cls.env["res.users"].create(
            {
                "name": "User Not In Group",
                "login": "user_not_in_group",
                "groups_id": [Command.set([base_user_group.id])],
            }
        )

    def test_no_restrictions_when_groups_empty(self):
        self.partner_model.write(
            {
                "duplicate_allowed_group_ids": [Command.clear()],
                "delete_allowed_group_ids": [Command.clear()],
            }
        )
        result = self.env["res.partner"].fields_view_get(view_type="form")
        arch = etree.fromstring(result["arch"])
        self.assertIsNone(arch.get("duplicate"))
        self.assertIsNone(arch.get("delete"))

    def test_duplicate_restriction_based_on_group_membership(self):
        """Test duplicate action restricted to specific group"""
        self.partner_model.write(
            {"duplicate_allowed_group_ids": [Command.set([self.test_group.id])]}
        )
        result = (
            self.env["res.partner"]
            .with_user(self.user_in_group)
            .fields_view_get(view_type="form")
        )
        arch = etree.fromstring(result["arch"])
        self.assertNotEqual(arch.get("duplicate"), "0")
        result = (
            self.env["res.partner"]
            .with_user(self.user_not_in_group)
            .fields_view_get(view_type="form")
        )
        arch = etree.fromstring(result["arch"])
        self.assertEqual(arch.get("duplicate"), "0")

    def test_delete_restriction_based_on_group_membership(self):
        """Test delete action restricted to specific group"""
        self.partner_model.write(
            {"delete_allowed_group_ids": [Command.set([self.test_group.id])]}
        )
        result = (
            self.env["res.partner"]
            .with_user(self.user_in_group)
            .fields_view_get(view_type="form")
        )
        arch = etree.fromstring(result["arch"])
        self.assertNotEqual(arch.get("delete"), "0")
        result = (
            self.env["res.partner"]
            .with_user(self.user_not_in_group)
            .fields_view_get(view_type="form")
        )
        arch = etree.fromstring(result["arch"])
        self.assertEqual(arch.get("delete"), "0")

    def test_both_actions_restricted(self):
        """Test both duplicate and delete actions restricted to specific group"""
        self.partner_model.write(
            {
                "duplicate_allowed_group_ids": [Command.set([self.test_group.id])],
                "delete_allowed_group_ids": [Command.set([self.test_group.id])],
            }
        )
        result = (
            self.env["res.partner"]
            .with_user(self.user_in_group)
            .fields_view_get(view_type="form")
        )
        arch = etree.fromstring(result["arch"])
        self.assertNotEqual(arch.get("duplicate"), "0")
        self.assertNotEqual(arch.get("delete"), "0")
        result = (
            self.env["res.partner"]
            .with_user(self.user_not_in_group)
            .fields_view_get(view_type="form")
        )
        arch = etree.fromstring(result["arch"])
        self.assertEqual(arch.get("duplicate"), "0")
        self.assertEqual(arch.get("delete"), "0")

    def test_delete_restriction_in_tree_view(self):
        """Test delete action restriction applies to tree view"""
        self.partner_model.write(
            {"delete_allowed_group_ids": [Command.set([self.test_group.id])]}
        )
        result = (
            self.env["res.partner"]
            .with_user(self.user_in_group)
            .fields_view_get(view_type="tree")
        )
        arch = etree.fromstring(result["arch"])
        self.assertNotEqual(arch.get("delete"), "0")
        result = (
            self.env["res.partner"]
            .with_user(self.user_not_in_group)
            .fields_view_get(view_type="tree")
        )
        arch = etree.fromstring(result["arch"])
        self.assertEqual(arch.get("delete"), "0")

    def test_duplicate_restriction_not_applied_in_tree_view(self):
        self.partner_model.write(
            {"duplicate_allowed_group_ids": [Command.set([self.test_group.id])]}
        )
        result = self.env["res.partner"].fields_view_get(view_type="tree")
        arch = etree.fromstring(result["arch"])
        self.assertIsNone(arch.get("duplicate"))

    def test_delete_restriction_in_kanban_view(self):
        """Test delete action restriction applies to kanban view"""
        self.partner_model.write(
            {"delete_allowed_group_ids": [Command.set([self.test_group.id])]}
        )
        result = (
            self.env["res.partner"]
            .with_user(self.user_in_group)
            .fields_view_get(view_type="kanban")
        )
        arch = etree.fromstring(result["arch"])
        self.assertNotEqual(arch.get("delete"), "0")
        result = (
            self.env["res.partner"]
            .with_user(self.user_not_in_group)
            .fields_view_get(view_type="kanban")
        )
        arch = etree.fromstring(result["arch"])
        self.assertEqual(arch.get("delete"), "0")

    def test_duplicate_restriction_not_applied_in_kanban_view(self):
        """Test duplicate restriction is not applied to kanban view"""
        self.partner_model.write(
            {"duplicate_allowed_group_ids": [Command.set([self.test_group.id])]}
        )
        result = self.env["res.partner"].fields_view_get(view_type="kanban")
        arch = etree.fromstring(result["arch"])
        self.assertIsNone(arch.get("duplicate"))
