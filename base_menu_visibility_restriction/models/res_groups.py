# Copyright 2025 SH Yumtown - Nick Li
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResGroups(models.Model):
    _inherit = "res.groups"

    excluded_menu_ids = fields.Many2many(
        comodel_name="ir.ui.menu",
        relation="ir_ui_menu_excluded_group_rel",
        column1="gid",
        column2="menu_id",
        string="Excluded Menus",
    )
