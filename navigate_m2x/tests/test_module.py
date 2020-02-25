# Copyright (C) 2020 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestModule(TransactionCase):

    def setUp(self):
        super().setUp()
        self.action_server = self.env.ref(
            "navigate_m2x.actions_server_navigate_partner_2_tags")
        self.users = self.env["res.users"].search([])

    def test_action_result(self):
        result = self.action_server.with_context(
            active_model="res.users",
            active_ids=self.users.ids).run()

        self.assertNotEqual(
            result.get("domain", False), False)
