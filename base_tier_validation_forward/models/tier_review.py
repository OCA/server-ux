# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class TierReview(models.Model):
    _inherit = "tier.review"
    _order = "sequence"

    name = fields.Char(compute="_compute_definition_data", store=True, readonly=False)
    status = fields.Selection(selection_add=[("forwarded", "Forwarded")],)
    review_type = fields.Selection(
        compute="_compute_definition_data", store=True, readonly=False,
    )
    reviewer_id = fields.Many2one(
        comodel_name="res.users",
        compute="_compute_definition_data",
        store=True,
        readonly=False,
    )
    reviewer_group_id = fields.Many2one(
        comodel_name="res.groups",
        compute="_compute_definition_data",
        store=True,
        readonly=False,
    )
    sequence = fields.Float()
    approve_sequence = fields.Boolean(
        compute="_compute_definition_data", store=True, readonly=False,
    )
    comment_option = fields.Selection(
        related="definition_id.comment_option", readonly=True
    )

    @api.depends(
        "definition_id.name",
        "definition_id.review_type",
        "definition_id.reviewer_id",
        "definition_id.comment_option",
        "definition_id.reviewer_group_id",
        "definition_id.approve_sequence",
    )
    def _compute_definition_data(self):
        for rec in self:
            rec.name = rec.definition_id.name
            rec.review_type = rec.definition_id.review_type
            rec.reviewer_id = rec.definition_id.reviewer_id
            rec.reviewer_group_id = rec.definition_id.reviewer_group_id
            rec.approve_sequence = rec.definition_id.approve_sequence
            rec.comment_option = rec.definition_id.comment_option
