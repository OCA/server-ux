# Copyright 2026 CIT Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from lxml import etree

from odoo import Command
from odoo.tests.common import TransactionCase


class TestBaseArchiveManager(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ModelAccess = cls.env["ir.model.access"]
        cls.Partner = cls.env["res.partner"]

        # Create groups
        cls.group_no_access = cls.env["res.groups"].create(
            {"name": "No Archive Access"}
        )
        cls.group_archive_only = cls.env["res.groups"].create(
            {"name": "Archive Only Access"}
        )
        cls.group_unarchive_only = cls.env["res.groups"].create(
            {"name": "Unarchive Only Access"}
        )
        cls.group_full_access = cls.env["res.groups"].create(
            {"name": "Full Archive Access"}
        )

        partner_model = cls.env["ir.model"]._get("res.partner")

        # Clear existing access rights to avoid interference from default permissions
        existing_access = cls.ModelAccess.search([("model_id", "=", partner_model.id)])
        existing_access.write(
            {
                "perm_archive": False,
                "perm_unarchive": False,
            }
        )

        # Create access rights for res.partner
        cls.ModelAccess.create(
            {
                "name": "No Access",
                "model_id": partner_model.id,
                "group_id": cls.group_no_access.id,
                "perm_read": True,
                "perm_write": True,
                "perm_archive": False,
                "perm_unarchive": False,
            }
        )

        cls.ModelAccess.create(
            {
                "name": "Archive Only",
                "model_id": partner_model.id,
                "group_id": cls.group_archive_only.id,
                "perm_read": True,
                "perm_write": True,
                "perm_archive": True,
                "perm_unarchive": False,
            }
        )

        cls.ModelAccess.create(
            {
                "name": "Unarchive Only",
                "model_id": partner_model.id,
                "group_id": cls.group_unarchive_only.id,
                "perm_read": True,
                "perm_write": True,
                "perm_archive": False,
                "perm_unarchive": True,
            }
        )

        cls.ModelAccess.create(
            {
                "name": "Full Access",
                "model_id": partner_model.id,
                "group_id": cls.group_full_access.id,
                "perm_read": True,
                "perm_write": True,
                "perm_archive": True,
                "perm_unarchive": True,
            }
        )

        # Create users
        cls.user_no_access = cls.env["res.users"].create(
            {
                "name": "User No Access",
                "login": "user_no_access",
                "groups_id": [
                    Command.set(
                        [cls.group_no_access.id, cls.env.ref("base.group_user").id]
                    )
                ],
            }
        )
        cls.user_archive_only = cls.env["res.users"].create(
            {
                "name": "User Archive Only",
                "login": "user_archive_only",
                "groups_id": [
                    Command.set(
                        [cls.group_archive_only.id, cls.env.ref("base.group_user").id]
                    )
                ],
            }
        )
        cls.user_unarchive_only = cls.env["res.users"].create(
            {
                "name": "User Unarchive Only",
                "login": "user_unarchive_only",
                "groups_id": [
                    Command.set(
                        [cls.group_unarchive_only.id, cls.env.ref("base.group_user").id]
                    )
                ],
            }
        )
        cls.user_full_access = cls.env["res.users"].create(
            {
                "name": "User Full Access",
                "login": "user_full_access",
                "groups_id": [
                    Command.set(
                        [cls.group_full_access.id, cls.env.ref("base.group_user").id]
                    )
                ],
            }
        )

    def test_get_archive_access(self):
        """Test the get_archive_access RPC method for all users."""
        res = self.ModelAccess.with_user(self.user_no_access).get_archive_access(
            "res.partner"
        )
        self.assertFalse(res["can_archive"])
        self.assertFalse(res["can_unarchive"])

        res = self.ModelAccess.with_user(self.user_archive_only).get_archive_access(
            "res.partner"
        )
        self.assertTrue(res["can_archive"])
        self.assertFalse(res["can_unarchive"])

        res = self.ModelAccess.with_user(self.user_unarchive_only).get_archive_access(
            "res.partner"
        )
        self.assertFalse(res["can_archive"])
        self.assertTrue(res["can_unarchive"])

        res = self.ModelAccess.with_user(self.user_full_access).get_archive_access(
            "res.partner"
        )
        self.assertTrue(res["can_archive"])
        self.assertTrue(res["can_unarchive"])

    def test_get_views(self):
        """Test get_views injection of invisible attributes."""
        views = [[False, "form"]]

        # Helper to get targeted elements in the arch
        def get_elements(user):
            res = self.Partner.with_user(user).get_views(views=views)
            arch = res["views"]["form"]["arch"]
            doc = etree.fromstring(arch)
            elements = doc.xpath("//button[@name='toggle_active']") + doc.xpath(
                "//field[@name='active']"
            )
            return elements, arch

        # 1. No access -> Should inject True
        elements_no, arch_no = get_elements(self.user_no_access)
        if elements_no:
            self.assertTrue(
                any("True" in el.get("invisible", "") for el in elements_no)
            )

        # 2. Archive only -> Should inject not active
        elements_ao, arch_ao = get_elements(self.user_archive_only)
        if elements_ao:
            self.assertTrue(
                any("not active" in el.get("invisible", "") for el in elements_ao)
            )

        # 3. Unarchive only -> Should inject active
        elements_uo, arch_uo = get_elements(self.user_unarchive_only)
        if elements_uo:
            for el in elements_uo:
                inv = el.get("invisible", "")
                if "active" in inv and "not active" not in inv:
                    break
            else:
                self.fail("Expected 'active' (and not 'not active') in invisible attr")

        # 4. Full access -> No injection
        elements_fa, arch_fa = get_elements(self.user_full_access)
        if elements_no:
            self.assertNotEqual(arch_fa, arch_no)
            self.assertNotEqual(arch_fa, arch_ao)
            self.assertNotEqual(arch_fa, arch_uo)

    def test_get_views_existing_and_new_invisible(self):
        """Test get_views when elements already have invisible vs. when they do not."""
        test_view = self.env["ir.ui.view"].create(
            {
                "name": "res.partner.test.form",
                "model": "res.partner",
                "type": "form",
                "arch": """
                    <form>
                        <field name="active" invisible="is_company"/>
                        <button name="toggle_active" type="object"/>
                    </form>
                """,
            }
        )

        res = self.Partner.with_user(self.user_archive_only).get_views(
            views=[[test_view.id, "form"]]
        )
        arch = res["views"]["form"]["arch"]
        doc = etree.fromstring(arch)

        # 1. Verify 'if existing:' branch -> combines expressions with 'or'
        field_elem = doc.xpath("//field[@name='active']")[0]
        self.assertEqual(
            field_elem.get("invisible"),
            "(is_company) or (not active)",
        )

        # 2. Verify 'else:' branch -> sets condition directly
        btn_elem = doc.xpath("//button[@name='toggle_active']")[0]
        self.assertEqual(
            btn_elem.get("invisible"),
            "not active",
        )

    def test_get_views_edge_cases(self):
        """Test get_views edge cases: no active_name, missing views, and empty arch."""
        res = (
            self.env["res.country"]
            .with_user(self.user_no_access)
            .get_views(views=[[False, "form"]])
        )
        self.assertIn("views", res)

        # Use a model without mail.thread inheritance to avoid mail_thread KeyError
        category = self.env["res.partner.category"].with_user(self.user_no_access)
        with (
            patch.object(
                type(self.env["ir.model.access"]), "check", return_value=False
            ),
            patch(
                "odoo.addons.base.models.ir_ui_view.Model.get_views",
                return_value={},
            ),
        ):
            res = category.get_views(views=[[False, "form"]])
            self.assertEqual(res, {})

        with (
            patch.object(
                type(self.env["ir.model.access"]), "check", return_value=False
            ),
            patch(
                "odoo.addons.base.models.ir_ui_view.Model.get_views",
                return_value={"views": {"form": {"arch": ""}}},
            ),
        ):
            res = category.get_views(views=[[False, "form"]])
            self.assertEqual(res["views"]["form"]["arch"], "")

    def test_get_views_unreachable_branch_fallback(self):
        class DynamicBool:
            def __init__(self, first_val, rest_val=True):
                self.first = True
                self.first_val = first_val
                self.rest_val = rest_val

            def __bool__(self):
                if self.first:
                    self.first = False
                    return self.first_val
                return self.rest_val

        def fake_check(model, mode, raise_exception=False):
            if mode == "archive":
                return DynamicBool(False, True)
            return True

        category = self.env["res.partner.category"].with_user(self.user_no_access)
        with patch.object(
            type(self.env["ir.model.access"]), "check", side_effect=fake_check
        ):
            res = category.get_views(views=[[False, "form"]])
            self.assertIn("views", res)
