# Copyright 2018 Onestein
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.addons.easy_switch_user.controllers.main import SwitchController


class TestController(TransactionCase):
    def test_switch(self):
        switch_controller = SwitchController()
        with self.assertRaises(Exception):
            switch_controller.switch('unknown_user', '1234567890')
