# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class BaseAutomation(models.Model):
    _inherit = "base.automation"

    subscribe_team_ids = fields.Many2many(
        comodel_name="crm.team",
        string="Add Sales Teams as Followers",
        help="All members of these teams will be added as followers.",
    )
