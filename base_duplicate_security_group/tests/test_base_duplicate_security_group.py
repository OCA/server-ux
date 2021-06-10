# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import common, tagged


@tagged('-at_install', 'post_install')
class TestDuplicateSecurityGroup(common.HttpCase):
    def setUp(self):
        super().setUp()
        self.user_admin = self.env.ref('base.user_admin')

    def test_duplicate_button(self):
        """Whether or not the duplicate button is available
        The button should be accessible depending on the user permissions."""
        self.browser_js(
            url_path="/web",
            code="odoo.__DEBUG__.services['web_tour.tour']"
                 ".run('button_duplicate_ok')",
            ready="odoo.__DEBUG__.services['web_tour.tour']."
                  "tours.button_duplicate_ok.ready",
            login="admin",
        )
        group = self.env.ref(
            "base_duplicate_security_group.group_duplicate_records"
        )
        group.users -= self.user_admin
        self.browser_js(
            url_path="/web",
            code="odoo.__DEBUG__.services['web_tour.tour']"
                 ".run('button_duplicate_ko')",
            ready="odoo.__DEBUG__.services['web_tour.tour']."
                  "tours.button_duplicate_ko.ready",
            login="admin",
        )
