# Copyright 2020 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestIrUiMenuCase(TransactionCase):
    def setUp(self):
        super().setUp()
        self.user_admin = self.browse_ref("base.user_admin").id
        self.group_hide_menu = self.env["res.groups"].create(
            {
                "name": "Hide menu items custom",
                "user_ids": [Command.link(self.user_admin)],
            }
        )
        self.model_ir_uir_menu = self.env["ir.ui.menu"]
        self.ir_ui_menu = self.browse_ref("base.menu_management")

    def test_ir_ui_menu_admin(self):
        items = self.model_ir_uir_menu.with_user(self.user_admin)._visible_menu_ids()
        self.assertTrue(self.ir_ui_menu.id in items)
        # Update ir_ui_menu to assign excluded_group_ids
        self.ir_ui_menu.write(
            {"excluded_group_ids": [Command.link(self.group_hide_menu.id)]}
        )
        items = self.model_ir_uir_menu.with_user(self.user_admin)._visible_menu_ids()
        self.assertTrue(self.ir_ui_menu.id not in items)

    def test_ir_ui_menu_excluded_by_implied_group(self):
        """The user belongs to the excluded group only through implied groups."""
        group_parent = self.env["res.groups"].create(
            {
                "name": "Group with implied",
                "implied_ids": [Command.link(self.group_hide_menu.id)],
            }
        )
        user = self.env["res.users"].create(
            {
                "name": "Implied group user",
                "login": "implied_group_user",
                "group_ids": [
                    Command.set([self.env.ref("base.group_system").id, group_parent.id])
                ],
            }
        )
        self.assertNotIn(self.group_hide_menu, user.group_ids)
        self.assertIn(self.group_hide_menu, user.all_group_ids)
        items = self.model_ir_uir_menu.with_user(user)._visible_menu_ids()
        self.assertIn(self.ir_ui_menu.id, items)
        self.ir_ui_menu.write(
            {"excluded_group_ids": [Command.link(self.group_hide_menu.id)]}
        )
        items = self.model_ir_uir_menu.with_user(user)._visible_menu_ids()
        self.assertNotIn(self.ir_ui_menu.id, items)
