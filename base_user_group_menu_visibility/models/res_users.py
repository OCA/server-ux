# Copyright 2023 Alexandre D. Díaz - Grupo Isonor
from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    is_system_user = fields.Boolean(compute="_compute_is_system_user")
    group_menu_visibility_ids = fields.Many2many(
        comodel_name="res.groups",
        relation="ir_ui_menu_res_users_group_visibility_rel",
        column1="menu_id",
        column2="gid",
        string="Group Menu Visibility",
    )

    def write(self, vals):
        if "group_menu_visibility_ids" in vals:
            self.env["ir.ui.menu"].clear_caches()
        return super().write(vals)

    def _compute_is_system_user(self):
        for user in self:
            user.is_system_user = user._is_system()
