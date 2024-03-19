# Copyright 2023 Alexandre D. Díaz - Grupo Isonor
from odoo import api, models, tools


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    @api.model
    @tools.ormcache(
        "frozenset(self.env.user.groups_id.ids)",
        "debug",
    )
    def _visible_menu_ids(self, debug=False):
        """Return the ids of the menu items visible to the user."""
        visible = super()._visible_menu_ids(debug=debug)
        if not self.env.user.group_menu_visibility_ids or self.env.user._is_system():
            return visible
        context = {"ir.ui.menu.full_list": True}
        menus = self.with_context(**context).browse(visible)
        groups = self.env.user.group_menu_visibility_ids
        visible = menus.filtered(lambda menu: menu.groups_id & groups)
        return set(visible.ids)
