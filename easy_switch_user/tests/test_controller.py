# Copyright 2018 Onestein
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.tests.common import TransactionCase
from odoo.addons.easy_switch_user.controllers.main import SwitchController


class FakeRequest(object):
    def __init__(self, env):
        self.db = env.cr.dbname
        self.session = FakeSession()


class FakeSession(object):
    def authenticate(self, db, login, password):
        return False


class TestController(TransactionCase):
    def setUp(self):
        super(TestController, self).setUp()
        self.ctrl = SwitchController()

    def test_switch(self):
        old_request = http.request
        http.request = FakeRequest(self.env)
        with self.assertRaises(Exception):
            self.ctrl.switch('unknown_user', '1234567890')
        http.request = old_request
