# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import HttpCase, tagged


@tagged("-at_install", "post_install")
class TestDuplicateSecurityGroup(HttpCase):
    def test_duplicate_button(self):
        """Whether or not the duplicate button is available
        The button should be accessible depending on the user permissions."""
        self.start_tour("web", "button_duplicate_ok", login="admin")
        group = self.env.ref("base_duplicate_security_group.group_duplicate_records")
        group.users -= self.env.ref("base.user_admin")
        self.start_tour("web", "button_duplicate_ko", login="admin")
