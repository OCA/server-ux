# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestModule(TransactionCase):
    def test_create_group(self):
        admin_user = self.env.ref("base.user_admin")
        ResGroups = self.env["res.groups"]

        admin_user.has_all_groups = True
        new_group = ResGroups.create({"name": "New Group 1"})
        self.assertIn(new_group.id, admin_user.groups_id.ids)

        admin_user.has_all_groups = False
        new_group = ResGroups.create({"name": "New Group 2"})
        self.assertNotIn(new_group.id, admin_user.groups_id.ids)
