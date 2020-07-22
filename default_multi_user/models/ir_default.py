# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class IrDefaultgard(models.Model):
    _inherit = "ir.default"

    user_ids = fields.Many2many(
        comodel_name="res.users",
        string="Users",
        relation="ir_default_res_users_rel",
        column1="ir_default_id",
        column2="res_users_id",
        compute="_compute_user_ids",
        store=True,
    )
    manual_user_ids = fields.Many2many(
        comodel_name="res.users",
        string="Available for Users",
        relation="ir_default_res_users_manual_rel",
    )
    group_ids = fields.Many2many(
        comodel_name="res.groups", string="Available for Groups",
    )

    @api.constrains("manual_user_ids", "group_ids")
    def _compute_user_ids(self):
        for rec in self:
            rec.user_ids = rec.manual_user_ids + rec.group_ids.users

    @api.model
    def _get_model_defaults_query_and_params(self, model_name, condition):
        query = """
            SELECT f.name, d.json_value FROM ir_default d
            JOIN ir_model_fields f ON d.field_id=f.id
            JOIN res_users u ON u.id=%s
            LEFT JOIN ir_default_res_users_rel m
                ON m.ir_default_id = d.id
            WHERE f.model=%s
                AND ((d.user_id IS NULL AND m.res_users_id IS NULL)
                     OR d.user_id=u.id OR m.res_users_id = u.id)
                AND (d.company_id IS NULL OR d.company_id=u.company_id)
                AND {}
            ORDER BY d.user_id, m.res_users_id, d.company_id, d.id
        """
        params = [self.env.uid, model_name]
        if condition:
            query = query.format("d.condition=%s")
            params.append(condition)
        else:
            query = query.format("d.condition IS NULL")
        return query, params
