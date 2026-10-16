# Copyright 2026 CIT Services
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResGroups(models.Model):
    _inherit = "res.groups"

    restricted_window_action_ids = fields.Many2many(
        comodel_name="ir.actions.act_window",
        relation="res_groups_restricted_window_action_rel",
        column1="gid",
        column2="act_id",
        string="Restricted Window Actions",
        help="Window actions restricted for members of this group.",
    )
    restricted_server_action_ids = fields.Many2many(
        comodel_name="ir.actions.server",
        relation="res_groups_restricted_server_action_rel",
        column1="gid",
        column2="act_id",
        string="Restricted Server Actions",
        help="Server actions restricted for members of this group.",
    )
