# Copyright 2026 CIT Services
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from lxml import etree

from odoo.exceptions import AccessError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestDuplicateAccess(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_model = cls.env["res.users"]
        cls.group_model = cls.env["res.groups"]
        cls.access_model = cls.env["ir.model.access"]
        cls.test_group = cls.group_model.create(
            {
                "name": "Test Group for Duplication",
            }
        )
        cls.group_user = cls.env.ref("base.group_user")

        cls.partner_model = cls.env["ir.model"].search(
            [("model", "=", "res.partner")], limit=1
        )
        cls.partner_access = cls.access_model.create(
            {
                "name": "Test Partner Access",
                "model_id": cls.partner_model.id,
                "group_id": cls.test_group.id,
                "perm_read": True,
                "perm_write": True,
                "perm_create": True,
                "perm_unlink": True,
                "perm_duplicate": False,
            }
        )

        cls.access_model.search(
            [
                ("model_id.model", "=", "res.partner"),
                ("group_id", "in", [cls.group_user.id, cls.test_group.id]),
            ]
        ).write({"perm_duplicate": False})

        cls.test_user = cls.user_model.create(
            {
                "name": "Test Duplication User",
                "login": "test_dup_user",
                "groups_id": [(6, 0, [cls.group_user.id, cls.test_group.id])],
            }
        )

    def test_duplicate_access_controls(self):
        partner = self.env["res.partner"].create({"name": "Original Partner"})
        with self.assertRaises(AccessError):
            partner.with_user(self.test_user).copy()
        result = (
            self.env["res.partner"].with_user(self.test_user).get_view(view_type="form")
        )
        arch = etree.fromstring(result["arch"])
        self.assertEqual(arch.get("duplicate"), "0")

        self.partner_access.write({"perm_duplicate": True})
        duplicated_partner = partner.with_user(self.test_user).copy()
        self.assertTrue(duplicated_partner)
        self.assertEqual(duplicated_partner.name, "Original Partner (copy)")
        result = (
            self.env["res.partner"].with_user(self.test_user).get_view(view_type="form")
        )
        arch = etree.fromstring(result["arch"])
        self.assertNotEqual(arch.get("duplicate"), "0")

    def test_duplicate_access_superuser(self):
        """Test that the superuser can duplicate records regardless of restrictions."""
        partner = self.env["res.partner"].create({"name": "Original Partner"})
        # As su, copying should succeed even if perm_duplicate
        # is False for all other groups
        duplicated_partner = partner.sudo().copy()
        self.assertTrue(duplicated_partner)
        self.assertEqual(duplicated_partner.name, "Original Partner (copy)")

    def test_duplicate_access_additive_permissions(self):
        """Test that if a user has multiple groups, and at least
        one grants duplicate permission, they can duplicate."""
        # Create a second group that will grant duplicate access
        group_grant = self.group_model.create(
            {
                "name": "Granting Group for Duplication",
            }
        )
        self.access_model.create(
            {
                "name": "Grant Partner Access",
                "model_id": self.partner_model.id,
                "group_id": group_grant.id,
                "perm_read": True,
                "perm_write": True,
                "perm_create": True,
                "perm_unlink": True,
                "perm_duplicate": True,
            }
        )

        # User is in both groups: test_group (perm_duplicate=False)
        # and group_grant (perm_duplicate=True)
        self.test_user.write(
            {
                "groups_id": [(4, group_grant.id)],
            }
        )

        partner = self.env["res.partner"].create({"name": "Original Partner"})

        # Copy should succeed because group_grant has perm_duplicate=True
        duplicated_partner = partner.with_user(self.test_user).copy()
        self.assertTrue(duplicated_partner)
        self.assertEqual(duplicated_partner.name, "Original Partner (copy)")
