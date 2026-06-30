# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResGroups(models.Model):
    _inherit = "res.groups"

    custom_search_model_ids = fields.Many2many(
        "ir.model",
        relation="custom_search_group_rel",
        string="Custom Search Models",
        help="Only users in this group will see the 'Add Custom Filter' and "
        "'Add Custom Group' options in the search view of the selected models.",
    )
