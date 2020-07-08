# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class IrFilters(models.Model):
    _inherit = "ir.filters"

    user_ids = fields.Many2many(
        comodel_name="res.users",
        string="Users",
    )

    @api.model
    def get_filters(self, model, action_id=None):
        # WARNING: this function overrides the standard one.
        # The only change done is in the domain used to search the filters.
        action_domain = self._get_action_domain(action_id)
        filters = self.search(action_domain + [
            ('model_id', '=', model),
            '|', ('user_id', 'in', [self._uid, False]),
            ('user_ids', 'in', self._uid),
        ])
        user_context = self.env['res.users'].context_get()
        return filters.with_context(user_context).read(
            ['name', 'is_default', 'domain', 'context', 'user_id', 'sort'])
