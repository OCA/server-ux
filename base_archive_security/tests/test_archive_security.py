# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import AccessError
from odoo.tests import TransactionCase


class TestArchiveSecurity(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = cls.env.ref("base_archive_security.group_can_archive")
        cls.record = cls.env["res.partner"].create({"name": "Test"})

    def test_user_allowed_by_default(self):
        """By default, all users can toggle_active"""
        self.record.toggle_active()

    def test_user_not_allowed(self):
        """User without permission cannot toggle_active"""
        self.env.user.groups_id -= self.group
        with self.assertRaises(AccessError):
            self.record.toggle_active()
