# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class IrFilters(models.Model):
    _inherit = "ir.filters"

    user_ids = fields.Many2many(
        comodel_name="res.users",
        string="Users",
        compute="_compute_user_ids",
        store=True,
    )
    manual_user_ids = fields.Many2many(
        comodel_name="res.users",
        string="Available for Users",
        relation="ir_filters_res_users_manual_rel",
    )
    group_ids = fields.Many2many(
        comodel_name="res.groups",
        string="Available for Groups",
    )

    @api.constrains("manual_user_ids", "group_ids")
    def _compute_user_ids(self):
        for rec in self:
            rec.user_ids = rec.manual_user_ids + rec.group_ids.users

    @api.model
    def get_filters(self, model, action_id=None):
        # WARNING: this function overrides the standard one.
        # The only change done is in the domain used to search the filters.
        action_domain = self._get_action_domain(action_id)
        filters = self.search(
            action_domain
            + [
                ("model_id", "=", model),
                "|",
                "|",
                ("user_id", "=", self._uid),
                ("user_ids", "in", self._uid),
                "&",
                ("user_id", "=", False),
                ("user_ids", "=", False),
            ]
        )
        user_context = self.env["res.users"].context_get()
        return filters.with_context(user_context).read(
            ["name", "is_default", "domain", "context", "user_id", "sort"]
        )
