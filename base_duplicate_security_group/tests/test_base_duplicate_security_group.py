# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import HttpCase, tagged


@tagged("-at_install", "post_install")
class TestDuplicateSecurityGroup(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_duplicate = cls.env.ref(
            "base_duplicate_security_group.group_duplicate_records"
        )
        cls.admin_user = cls.env.ref("base.user_admin")

    def test_duplicate_button(self):
        """Test duplicate button availability in form view.
        The button should be accessible depending on the user permissions."""
        self.start_tour("web", "button_duplicate_ok", login="admin")
        self.group_duplicate.users -= self.admin_user
        self.start_tour("web", "button_duplicate_ko", login="admin")
        # Restore permissions for other tests
        self.group_duplicate.users |= self.admin_user
