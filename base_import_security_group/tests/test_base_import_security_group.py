# Copyright 2017 Onestein (http://www.onestein.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests import common, tagged
from odoo.tools import mute_logger


@tagged("post_install", "-at_install")
class TestImportSecurityGroup(common.HttpCase):
    def setUp(self):
        super().setUp()
        self.Access = self.env["ir.model.access"]
        self.user_test = self.env.ref("base.user_demo")
        self.user_admin = self.env.ref("base.user_admin")

    def has_button_import(self, falsify=False, user=None):
        """
        Verify that the Import button is either visible or invisible.
        """
        code = """
        window.setTimeout(function () {
            if (%s$('.o_button_import').length) {
                console.log('ok');
            } else {
                console.log('error');
            };
        }, 2000);
        """ % (
            "!" if falsify else ""
        )
        action = self.env.ref("base.action_partner_category_form").id
        link = "/web#action=%s" % action
        self.browser_js(
            link,
            code,
            'Boolean($(".o_list_button_add"))',
            login=user.login,
            timeout=2000,
        )

    def test_01_load(self):
        """ Admin user can import data, but the demo user cannot """
        fields = (
            "id",
            "name",
            "perm_read",
            "perm_write",
            "perm_create",
            "perm_unlink",
        )
        data = [
            ("access_res_users_test", "res.users test", "1", "0", "0", "0"),
            ("access_res_users_test2", "res.users test2", "1", "1", "1", "1"),
        ]
        self.has_button_import(user=self.user_admin)
        with mute_logger("odoo.sql_db"):
            res = self.Access.with_user(self.user_admin).load(fields, data)

        self.assertEqual(res["ids"], False)
        self.assertEqual(len(res["messages"]), 2)
        self.assertEqual(
            res["messages"][0]["message"],
            "Missing required value for the field 'Model' (model_id)",
        )
        self.assertEqual(
            res["messages"][1]["message"],
            "Missing required value for the field 'Model' (model_id)",
        )

        self.has_button_import(falsify=True, user=self.user_test)
        res2 = self.Access.with_user(self.user_test).load(fields, data)

        self.assertEqual(res2["ids"], None)
        self.assertEqual(len(res2["messages"]), 1)
        self.assertEqual(
            res2["messages"][0]["message"],
            "User (ID: %s) is not allowed to import data in "
            "model ir.model.access." % self.user_test.id,
        )
