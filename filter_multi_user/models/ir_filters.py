# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class IrFilters(models.Model):
    _inherit = "ir.filters"

    # user_ids is now a native Many2many on ir.filters in v19.
    # We compute its value from manual_user_ids + group_ids.users via constrains.

    manual_user_ids = fields.Many2many(
        comodel_name="res.users",
        string="Available for Users",
        relation="ir_filters_res_users_manual_rel",
    )
    group_ids = fields.Many2many(
        comodel_name="res.groups",
        string="Available for Groups",
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._sync_user_ids()
        return records

    def write(self, vals):
        result = super().write(vals)
        if "manual_user_ids" in vals or "group_ids" in vals:
            self._sync_user_ids()
        return result

    def _sync_user_ids(self):
        for rec in self:
            rec.user_ids = rec.manual_user_ids | rec.group_ids.user_ids
