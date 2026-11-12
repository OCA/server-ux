# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestExportManagerJs(HttpCase):
    def test_unit_desktop(self):
        self.browser_js(
            "/web/tests?headless&loglevel=2&preset=desktop&timeout=15000"
            "&filter=base_export_manager",
            "",
            "",
            login="admin",
            timeout=1800,
            success_signal="[HOOT] Test suite succeeded",
            error_checker=lambda message: "[HOOT]" not in message,
        )
