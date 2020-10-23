# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json

from odoo.tests import common


class TestDefaultMultiUser(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(cls.env.context, tracking_disable=True, no_reset_password=True)
        )
        cls.default_model = cls.env["ir.default"]
        cls.user_model = cls.env["res.users"]
        cls.partner_model = cls.env["res.partner"]
        cls.company_model = cls.env["res.company"]

        cls.main_company = cls.env.ref("base.main_company")
        cls.other_company = cls.company_model.create({"name": "Test Company"})

        cls.field = cls.env.ref("base.field_res_partner__phone")
        cls.group_user = cls.env.ref("base.group_user")
        cls.group_partner = cls.env.ref("base.group_partner_manager")
        cls.group_private = cls.env["res.groups"].create({"name": "Test Group"})

        cls.user_1 = cls._create_user(
            "user_1", [cls.group_user, cls.group_partner, cls.group_private]
        )
        cls.user_2 = cls._create_user("user_2", [cls.group_user, cls.group_partner])
        cls.user_3 = cls._create_user(
            "user_3", [cls.group_user, cls.group_partner, cls.group_private]
        )
        cls.user_4 = cls._create_user(
            "user_4",
            [cls.group_user, cls.group_partner, cls.group_private],
            cls.other_company,
        )

        cls.test_value = "+34 666 777 888"

    @classmethod
    def _create_user(cls, login, groups, company=False):
        if not company:
            company = cls.main_company
        group_ids = [group.id for group in groups]
        user = cls.user_model.create(
            {
                "name": "Test User",
                "login": login,
                "password": "demo",
                "email": "%s@yourcompany.com" % login,
                "groups_id": [(6, 0, group_ids)],
                "company_id": company.id,
                "company_ids": [(6, 0, [cls.main_company.id, cls.other_company.id])],
            }
        )
        return user

    def test_01_no_multi_user(self):
        self.default_model.create(
            {
                "field_id": self.field.id,
                "json_value": json.dumps(self.test_value, ensure_ascii=False),
                "user_id": self.user_1.id,
            }
        )
        rec_1 = self.partner_model.with_user(self.user_1).create({"name": "Test"})
        self.assertEqual(rec_1.phone, self.test_value)
        rec_2 = self.partner_model.with_user(self.user_2).create({"name": "Test"})
        self.assertNotEqual(rec_2.phone, self.test_value)

    def test_02_multi_user(self):
        test_default = self.default_model.create(
            {
                "field_id": self.field.id,
                "json_value": json.dumps(self.test_value, ensure_ascii=False),
                "user_id": self.user_1.id,
                "manual_user_ids": [(6, 0, (self.user_1 + self.user_2).ids)],
            }
        )
        self.assertIn(self.user_1, test_default.user_ids)
        self.assertIn(self.user_2, test_default.user_ids)
        rec_1 = self.partner_model.with_user(self.user_1).create({"name": "Test"})
        self.assertEqual(rec_1.phone, self.test_value)
        rec_2 = self.partner_model.with_user(self.user_2).create({"name": "Test"})
        self.assertEqual(rec_2.phone, self.test_value)

    def test_03_group_default(self):
        # Global default - expected for user 2
        global_value = "+01 564 879 123"
        self.default_model.create(
            {
                "field_id": self.field.id,
                "json_value": json.dumps(global_value, ensure_ascii=False),
            }
        )
        # Group specific default - expected for user 1 and 3
        test_default = self.default_model.create(
            {
                "field_id": self.field.id,
                "json_value": json.dumps(self.test_value, ensure_ascii=False),
                "group_ids": [(6, 0, self.group_private.ids)],
            }
        )
        self.assertIn(self.user_1, test_default.user_ids)
        self.assertIn(self.user_3, test_default.user_ids)
        rec_1 = self.partner_model.with_user(self.user_1).create({"name": "Test"})
        self.assertEqual(rec_1.phone, self.test_value)
        rec_2 = self.partner_model.with_user(self.user_2).create({"name": "Test"})
        self.assertEqual(rec_2.phone, global_value)
        rec_3 = self.partner_model.with_user(self.user_3).create({"name": "Test"})
        self.assertEqual(rec_3.phone, self.test_value)

    def test_04_multi_user_no_alternative(self):
        test_default = self.default_model.create(
            {
                "field_id": self.field.id,
                "json_value": json.dumps(self.test_value, ensure_ascii=False),
                "manual_user_ids": [(6, 0, self.user_2.ids)],
            }
        )
        self.assertNotIn(self.user_1, test_default.user_ids)
        self.assertIn(self.user_2, test_default.user_ids)
        rec_1 = self.partner_model.with_user(self.user_1).create({"name": "Test"})
        self.assertNotEqual(rec_1.phone, self.test_value)
        rec_2 = self.partner_model.with_user(self.user_2).create({"name": "Test"})
        self.assertEqual(rec_2.phone, self.test_value)

    def test_05_multi_company(self):
        # Global for main company
        self.default_model.create(
            {
                "field_id": self.field.id,
                "json_value": json.dumps(self.test_value, ensure_ascii=False),
                "company_id": self.main_company.id,
            }
        )
        rec_1 = self.partner_model.with_user(self.user_2).create({"name": "Test"})
        self.assertEqual(rec_1.phone, self.test_value)
        # User in other company does not get the default.
        rec_2 = self.partner_model.with_user(self.user_4).create({"name": "Test"})
        self.assertNotEqual(rec_2.phone, self.test_value)
        # User 1 switch company. Does not get the default.
        self.user_1.company_id = self.other_company
        rec_3 = self.partner_model.with_user(self.user_1).create({"name": "Test"})
        self.assertNotEqual(rec_3.phone, self.test_value)
