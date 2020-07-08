# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common
from odoo.exceptions import AccessError


class TestFilterMultiUser(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.filter_model = cls.env["ir.filters"]
        cls.user_model = cls.env["res.users"]

        cls.group_user = cls.env.ref("base.group_user")

        cls.user_1 = cls._create_user("user_1", [cls.group_user])
        cls.user_2 = cls._create_user("user_2", [cls.group_user])

    @classmethod
    def _create_user(self, login, groups):
        group_ids = [group.id for group in groups]
        user = self.user_model.with_context({"no_reset_password": True}).create({
            "name": "Test User",
            "login": login,
            "password": "demo",
            "email": "%s@yourcompany.com" % login,
            "groups_id": [(6, 0, group_ids)]
        })
        return user

    def test_01_no_multi_user(self):
        test_filter = self.filter_model.create({
            "name": "Test filter",
            "model_id": "ir.filters",
            "user_id": self.user_1.id,
        })
        self.assertTrue(test_filter.sudo(self.user_1).name)
        with self.assertRaises(AccessError):
            self.assertTrue(test_filter.sudo(self.user_2).name)

    def test_02_multi_user(self):
        test_filter = self.filter_model.create({
            "name": "Test filter",
            "model_id": "ir.filters",
            "user_id": self.user_1.id,
            "user_ids": [(6, 0, (self.user_1 + self.user_2).ids)],
        })
        self.assertTrue(test_filter.sudo(self.user_1).name)
        self.assertTrue(test_filter.sudo(self.user_2).name)

    def test_02_get_filters(self):
        test_filter_1 = self.filter_model.create({
            "name": "Test filter",
            "model_id": "ir.filters",
            "user_id": self.user_1.id,
            "user_ids": [(6, 0, (self.user_1 + self.user_2).ids)],
        })
        test_filter_2 = self.filter_model.create({
            "name": "Test filter 2",
            "model_id": "ir.filters",
            "user_id": self.user_1.id,
        })
        # User 1:
        res = self.filter_model.sudo(self.user_1).get_filters("ir.filters")
        result = []
        for filter in res:
            result.append(filter.get("id"))
        self.assertIn(test_filter_1.id, result)
        self.assertIn(test_filter_2.id, result)
        # User 2:
        res = self.filter_model.sudo(self.user_2).get_filters("ir.filters")
        result = []
        for filter in res:
            result.append(filter.get("id"))
        self.assertIn(test_filter_1.id, result)
        self.assertNotIn(test_filter_2.id, result)
