# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import AccessError
from odoo.tests import common


class TestFilterMultiUser(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(cls.env.context, tracking_disable=True, no_reset_password=True)
        )
        cls.filter_model = cls.env["ir.filters"]
        cls.user_model = cls.env["res.users"]

        cls.group_user = cls.env.ref("base.group_user")
        cls.group_private = cls.env["res.groups"].create({"name": "Test Group"})

        cls.user_1 = cls._create_user("user_1", [cls.group_user, cls.group_private])
        cls.user_2 = cls._create_user("user_2", [cls.group_user])
        cls.user_3 = cls._create_user("user_3", [cls.group_user, cls.group_private])

    @classmethod
    def _create_user(cls, login, groups):
        group_ids = [group.id for group in groups]
        user = cls.user_model.create(
            {
                "name": "Test User",
                "login": login,
                "password": "demo",
                "email": "%s@yourcompany.com" % login,
                "groups_id": [(6, 0, group_ids)],
            }
        )
        return user

    def test_01_no_multi_user(self):
        test_filter = self.filter_model.create(
            {
                "name": "Test filter",
                "model_id": "ir.filters",
                "user_id": self.user_1.id,
            }
        )
        self.assertTrue(test_filter.with_user(self.user_1).name)
        test_filter.invalidate_recordset()
        with self.assertRaises(AccessError):
            self.assertTrue(test_filter.with_user(self.user_2).name)

    def test_02_multi_user(self):
        test_filter = self.filter_model.create(
            {
                "name": "Test filter",
                "model_id": "ir.filters",
                "user_id": self.user_1.id,
                "manual_user_ids": [(6, 0, (self.user_1 + self.user_2).ids)],
            }
        )
        self.assertTrue(test_filter.with_user(self.user_1).name)
        test_filter.invalidate_recordset()
        self.assertTrue(test_filter.with_user(self.user_2).name)

    def test_03_get_filters(self):
        test_filter_1 = self.filter_model.create(
            {
                "name": "Test filter - specific user",
                "model_id": "ir.filters",
                "manual_user_ids": [(6, 0, (self.user_1 + self.user_2).ids)],
            }
        )
        test_filter_2 = self.filter_model.create(
            {
                "name": "Test filter 2 - Regular",
                "model_id": "ir.filters",
                "user_id": self.user_1.id,
            }
        )
        test_filter_3 = self.filter_model.create(
            {
                "name": "Test filter 3 - Group",
                "model_id": "ir.filters",
                "user_id": self.user_1.id,
                "group_ids": [(6, 0, self.group_private.ids)],
            }
        )
        # User 1:
        res = self.filter_model.with_user(self.user_1).get_filters("ir.filters")
        result = []
        for filters in res:
            result.append(filters.get("id"))
        self.assertIn(test_filter_1.id, result)
        self.assertIn(test_filter_2.id, result)
        self.assertIn(test_filter_3.id, result)
        # User 2:
        res = self.filter_model.with_user(self.user_2).get_filters("ir.filters")
        result = []
        for filters in res:
            result.append(filters.get("id"))
        self.assertIn(test_filter_1.id, result)
        self.assertNotIn(test_filter_2.id, result)
        self.assertNotIn(test_filter_3.id, result)
        # User 3:
        res = self.filter_model.with_user(self.user_3).get_filters("ir.filters")
        result = []
        for filters in res:
            result.append(filters.get("id"))
        self.assertNotIn(test_filter_1.id, result)
        self.assertNotIn(test_filter_2.id, result)
        self.assertIn(test_filter_3.id, result)

    def test_04_group_filter(self):
        test_filter = self.filter_model.create(
            {
                "name": "Test filter",
                "model_id": "ir.filters",
                "user_id": self.user_1.id,
                "group_ids": [(6, 0, self.group_private.ids)],
            }
        )
        self.assertTrue(test_filter.with_user(self.user_1).name)
        test_filter.invalidate_recordset()
        with self.assertRaises(AccessError):
            self.assertTrue(test_filter.with_user(self.user_2).name)
        test_filter.invalidate_recordset()
        self.assertTrue(test_filter.with_user(self.user_3).name)
