# Copyright 2026 CIT Services
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResGroups(models.Model):
    _inherit = "res.groups"

    restricted_report_action_ids = fields.Many2many(
        comodel_name="ir.actions.report",
        relation="res_groups_restricted_report_action_rel",
        column1="gid",
        column2="act_id",
        string="Restricted Report Actions",
        help="Report actions restricted for members of this group.",
    )
