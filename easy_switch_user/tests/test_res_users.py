# Copyright 2018 Onestein
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install", "res_users")
class TestResUsers(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.admin_user = cls.env.ref("base.user_admin")
        cls.demo_user = cls.env.ref("base.user_demo")
        cls.view_action = cls.env.ref("base.action_res_users")

    def test_01_switch_user(self):
        """Test the steps to switch the users to log in as the demo user"""
        tour_name = "easy_switch_user.test_switch_user"
        url_path = "web#id=%s&action=%s&model=res.users&view_type=form" % (
            self.demo_user.id,
            self.view_action.id,
        )
        self.start_tour(
            url_path=url_path,
            tour_name=tour_name,
            login=self.admin_user.login,
        )
