# Copyright 2020 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestIrUiMenuCase(TransactionCase):
    def setUp(self):
        super(TestIrUiMenuCase, self).setUp()
        self.user_admin = self.browse_ref("base.user_admin").id
        self.group_hide_menu = self.env["res.groups"].create(
            {"name": "Hide menu items custom", "users": [(4, self.user_admin)]}
        )
        self.model_ir_uir_menu = self.env["ir.ui.menu"]
        self.ir_ui_menu = self.browse_ref("base.menu_management")

    def test_ir_ui_menu_admin(self):
        items = self.model_ir_uir_menu.with_user(self.user_admin)._visible_menu_ids()
        self.assertTrue(self.ir_ui_menu.id in items)
        # Update ir_ui_menu to assign excluded_group_ids
        self.ir_ui_menu.write({"excluded_group_ids": [(4, self.group_hide_menu.id)]})
        items = self.model_ir_uir_menu.with_user(self.user_admin)._visible_menu_ids()
        self.assertTrue(self.ir_ui_menu.id not in items)
