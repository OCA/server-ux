# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestSystray(HttpCase):
    def test_review_menu(self):
        """Run the QUnit tests of the review menu."""
        self.browser_js(
            "/web/tests?debug=assets&module=base_tier_validation",
            "",
            login="admin",
        )
