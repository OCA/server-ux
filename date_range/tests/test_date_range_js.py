# Copyright 2026 Tecnativa - Carlos Lopez
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestDateRangeJs(HttpCase):
    def test_js_unit_tests(self):
        self.browser_js(
            "/web/tests?filter=date_range.condition_tree",
            "",
            login="admin",
            timeout=1800,
        )
