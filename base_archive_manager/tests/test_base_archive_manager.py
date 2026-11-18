# Copyright 2026 CIT Services
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from lxml import etree

from odoo.exceptions import AccessError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestArchiveUnarchiveAccess(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_model = cls.env["res.users"]
        cls.group_model = cls.env["res.groups"]
        cls.access_model = cls.env["ir.model.access"]

        cls.group_user = cls.env.ref("base.group_user")

        cls.group_no_access = cls.group_model.create({"name": "No Archive Access"})
        cls.group_archive_only = cls.group_model.create({"name": "Archive Only Access"})
        cls.group_unarchive_only = cls.group_model.create(
            {"name": "Unarchive Only Access"}
        )
        cls.group_full_access = cls.group_model.create({"name": "Full Archive Access"})

        cls.partner_model = cls.env["ir.model"].search(
            [("model", "=", "res.partner")], limit=1
        )

        existing_rules = cls.access_model.search(
            [("model_id", "=", cls.partner_model.id)]
        )
        existing_rules.write({"perm_archive": False, "perm_unarchive": False})
        cls.partner_no_access = cls.access_model.create(
            {
                "name": "No Access",
                "model_id": cls.partner_model.id,
                "group_id": cls.group_no_access.id,
                "perm_read": True,
                "perm_write": True,
                "perm_archive": False,
                "perm_unarchive": False,
            }
        )

        cls.partner_archive_access = cls.access_model.create(
            {
                "name": "No Access",
                "model_id": cls.partner_model.id,
                "group_id": cls.group_archive_only.id,
                "perm_read": True,
                "perm_write": True,
                "perm_archive": True,
                "perm_unarchive": False,
            }
        )

        cls.partner_unarchive_access = cls.access_model.create(
            {
                "name": "No Access",
                "model_id": cls.partner_model.id,
                "group_id": cls.group_unarchive_only.id,
                "perm_read": True,
                "perm_write": True,
                "perm_archive": False,
                "perm_unarchive": True,
            }
        )

        cls.partner_full_access = cls.access_model.create(
            {
                "name": "No Access",
                "model_id": cls.partner_model.id,
                "group_id": cls.group_full_access.id,
                "perm_read": True,
                "perm_write": True,
                "perm_archive": True,
                "perm_unarchive": True,
            }
        )

        cls.user_no_access = cls.env["res.users"].create(
            {
                "name": "User No Access",
                "login": "user_no_access",
                "groups_id": [
                    (6, 0, [cls.group_user.id, cls.group_no_access.id]),
                ],
            }
        )

        cls.user_archive_only = cls.env["res.users"].create(
            {
                "name": "User Archive Access",
                "login": "user_archive_access",
                "groups_id": [
                    (6, 0, [cls.group_user.id, cls.group_archive_only.id]),
                ],
            }
        )

        cls.user_unarchive_only = cls.env["res.users"].create(
            {
                "name": "User Unarchive Access",
                "login": "user_unarchive_access",
                "groups_id": [
                    (6, 0, [cls.group_user.id, cls.group_unarchive_only.id]),
                ],
            }
        )

        cls.user_full_access = cls.env["res.users"].create(
            {
                "name": "User Full Access",
                "login": "user_full_access",
                "groups_id": [
                    (6, 0, [cls.group_user.id, cls.group_full_access.id]),
                ],
            }
        )

        cls.Partner = cls.env["res.partner"]

    def test_check_archive_access_no_access(self):
        access_model = self.access_model.with_user(self.user_no_access)
        with self.assertRaises(AccessError):
            access_model._check_archive_access("res.partner")

    def test_check_archive_access_no_access_no_raise(self):
        access_model = self.access_model.with_user(self.user_no_access)
        result = access_model._check_archive_access(
            "res.partner", raise_exception=False
        )
        self.assertFalse(result)

    def test_check_archive_access_archive_only(self):
        access_model = self.access_model.with_user(self.user_archive_only)
        result = access_model._check_archive_access(
            "res.partner", raise_exception=False
        )
        self.assertTrue(result)

    def test_check_archive_access_unarchive_only(self):
        access_model = self.access_model.with_user(self.user_unarchive_only)
        result = access_model._check_archive_access(
            "res.partner", raise_exception=False
        )
        self.assertFalse(result)

    def test_check_archive_access_full_access(self):
        access_model = self.access_model.with_user(self.user_full_access)
        result = access_model._check_archive_access(
            "res.partner", raise_exception=False
        )
        self.assertTrue(result)

    def test_check_unarchive_access_no_access(self):
        access_model = self.access_model.with_user(self.user_no_access)
        with self.assertRaises(AccessError):
            access_model._check_unarchive_access("res.partner")

    def test_check_unarchive_access_no_access_no_raise(self):
        access_model = self.access_model.with_user(self.user_no_access)
        result = access_model._check_unarchive_access(
            "res.partner", raise_exception=False
        )
        self.assertFalse(result)

    def test_check_unarchive_access_archive_only(self):
        access_model = self.access_model.with_user(self.user_archive_only)
        result = access_model._check_unarchive_access(
            "res.partner", raise_exception=False
        )
        self.assertFalse(result)

    def test_check_unarchive_access_unarchive_only(self):
        access_model = self.access_model.with_user(self.user_unarchive_only)
        result = access_model._check_unarchive_access(
            "res.partner", raise_exception=False
        )
        self.assertTrue(result)

    def test_check_unarchive_access_full_access(self):
        access_model = self.access_model.with_user(self.user_full_access)
        result = access_model._check_unarchive_access(
            "res.partner", raise_exception=False
        )
        self.assertTrue(result)

    def test_superuser_bypasses_archive_check(self):
        result = self.access_model.sudo()._check_archive_access("res.partner")
        self.assertTrue(result)

    def test_superuser_bypasses_unarchive_check(self):
        result = self.access_model.sudo()._check_unarchive_access("res.partner")
        self.assertTrue(result)

    def _get_root_view_element(self, user, view_type="form"):
        res = self.Partner.with_user(user).get_views(views=[[False, view_type]])
        arch = res["views"][view_type]["arch"]
        return etree.fromstring(arch)

    def test_get_views_no_access_sets_archive_and_unarchive_zero(self):
        root = self._get_root_view_element(self.user_no_access)
        self.assertEqual(root.get("archive"), "0")
        self.assertEqual(root.get("unarchive"), "0")

    def test_get_views_archive_only_sets_unarchive_zero(self):
        root = self._get_root_view_element(self.user_archive_only)
        self.assertNotEqual(root.get("archive"), "0")
        self.assertEqual(root.get("unarchive"), "0")

    def test_get_views_unarchive_only_sets_archive_zero(self):
        root = self._get_root_view_element(self.user_unarchive_only)
        self.assertEqual(root.get("archive"), "0")
        self.assertNotEqual(root.get("unarchive"), "0")

    def test_get_views_full_access_no_restrictions(self):
        root = self._get_root_view_element(self.user_full_access)
        self.assertNotEqual(root.get("archive"), "0")
        self.assertNotEqual(root.get("unarchive"), "0")
