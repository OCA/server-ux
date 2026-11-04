# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IrModel(models.Model):
    _inherit = "ir.model"

    duplicate_allowed_group_ids = fields.Many2many(
        "res.groups",
        "ir_model_duplicate_group_rel",
        "model_id",
        "group_id",
        string="Duplicate Allowed Groups",
        help="Restrict the 'Duplicate' action in form views to these groups. "
        "Leave empty to allow all users to duplicate records.",
    )
    delete_allowed_group_ids = fields.Many2many(
        "res.groups",
        "ir_model_delete_group_rel",
        "model_id",
        "group_id",
        string="Delete Allowed Groups",
        help="Restrict the 'Delete' action in form, tree, and kanban views to these groups. "
        "Leave empty to allow all users to delete records.",
    )
