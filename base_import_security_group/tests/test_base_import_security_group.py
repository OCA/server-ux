# Copyright 2017 Onestein (http://www.onestein.eu)
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests import common, tagged
from odoo.tools import mute_logger


@tagged("-at_install", "post_install")
class TestImportSecurityGroup(common.HttpCase):
    def setUp(self):
        super().setUp()
        self.Access = self.env["ir.model.access"]
        self.user_test = self.env["res.users"].create(
            {
                "name": "Test User",
                "login": "test_import_user",
                "email": "test_import_user@example.com",
                "group_ids": [(4, self.env.ref("base.group_user").id)],
            }
        )
        self.user_admin = self.env.ref("base.user_admin")
        self.fields = (
            "id",
            "name",
            "perm_read",
            "perm_write",
            "perm_create",
            "perm_unlink",
        )
        self.data = [
            ("access_res_users_test", "res.users test", "1", "0", "0", "0"),
            ("access_res_users_test2", "res.users test2", "1", "1", "1", "1"),
        ]

    def test_import_button(self):
        """Admin user has access to the import button by default"""
        self.start_tour("/web", "button_import_ok", login="admin")

    def test_no_import_button(self):
        """When removed from group, admin user has no access to the import button"""
        group = self.env.ref("base_import_security_group.group_import_csv")
        group.user_ids -= self.user_admin
        self.start_tour("/web", "button_import_ko", login="admin")

    def test_access_admin(self):
        """Admin user can import data"""
        with mute_logger("odoo.sql_db"):
            res = self.Access.with_user(self.user_admin).load(self.fields, self.data)
        self.assertEqual(res["ids"], False)
        self.assertEqual(len(res["messages"]), 2)
        self.assertIn(
            "Missing required value for the field 'Model' (model_id)",
            res["messages"][0]["message"],
        )
        self.assertIn(
            "Missing required value for the field 'Model' (model_id)",
            res["messages"][1]["message"],
        )

    def test_access_demo(self):
        """Demo user cannot import data"""
        self.user_test.write({"group_ids": [(4, self.ref("base.group_system"))]})
        self.start_tour("/web", "button_import_ko", login="test_import_user")
        res2 = self.Access.with_user(self.user_test).load(self.fields, self.data)
        self.assertEqual(res2["ids"], None)
        self.assertEqual(len(res2["messages"]), 1)
        self.assertEqual(
            res2["messages"][0]["message"],
            f"User (ID: {self.user_test.id}) is not allowed to import data in "
            "model ir.model.access.",
        )
