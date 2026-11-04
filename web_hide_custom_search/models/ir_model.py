# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class IrModel(models.Model):
    _inherit = "ir.model"

    custom_search_group_ids = fields.Many2many(
        "res.groups",
        string="Custom Search Groups",
        relation="custom_search_group_rel",
        help="If set, only users in these groups will see the 'Add Custom Filter' "
        "and 'Add Custom Group' options in the search view for this model.",
    )

    @api.model
    def is_custom_search_visible(self, model_name):
        model = self.sudo().search([("model", "=", model_name)], limit=1)
        groups = model.custom_search_group_ids
        if not model or not groups or self.env.user in groups.users:
            return True
        return False
