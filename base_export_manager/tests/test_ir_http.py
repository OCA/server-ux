# Copyright 2026 OCA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json

from odoo.tests import HttpCase, new_test_user


class TestIrHttp(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = new_test_user(
            cls.env,
            login="export-user",
            groups="base.group_user,base.group_allow_export",
            password="test-export-user",
        )

    def test_session_info_includes_export_models(self):
        self.authenticate(self.user.login, "test-export-user")
        response = self.url_open(
            "/web/session/get_session_info",
            data=json.dumps({"jsonrpc": "2.0", "method": "call", "id": "test"}),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("ir.exports", response.json()["result"]["export_models"])
