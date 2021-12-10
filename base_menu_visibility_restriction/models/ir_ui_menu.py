# Copyright 2020 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, tools


class IrUiMenu(models.Model):

    _inherit = "ir.ui.menu"

    excluded_group_ids = fields.Many2many(
        comodel_name="res.groups",
        relation="ir_ui_menu_excluded_group_rel",
        column1="menu_id",
        column2="gid",
        string="Excluded Groups",
    )

    @api.model
    @tools.ormcache("frozenset(self.env.user.groups_id.ids)", "debug")
    def _visible_menu_ids(self, debug=False):
        """Return the ids of the menu items visible to the user."""
        visible = super()._visible_menu_ids(debug=debug)
        context = {"ir.ui.menu.full_list": True}
        menus = self.with_context(context).browse(visible)
        groups = self.env.user.groups_id
        visible = menus - menus.filtered(lambda menu: menu.excluded_group_ids & groups)
        return set(visible.ids)
