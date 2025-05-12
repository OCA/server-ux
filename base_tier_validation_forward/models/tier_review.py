# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class TierReview(models.Model):
    _inherit = "tier.review"
    _order = "sequence"

    # NOTE: Added translate=True because in the compute method we assign:
    #   rec.name = rec.definition_id.name
    # And the field `name` in `tier.definition` is translated (translate=True),
    # so we must match this behavior.
    # Reference: https://github.com/OCA/server-ux/pull/1065#discussion_r2058502638
    name = fields.Char(
        compute="_compute_definition_data", store=True, related=False, translate=True
    )
    status = fields.Selection(
        selection_add=[("forwarded", "Forwarded")],
    )
    review_type = fields.Selection(
        compute="_compute_definition_data",
        store=True,
    )
    reviewer_id = fields.Many2one(
        comodel_name="res.users",
        compute="_compute_definition_data",
        store=True,
    )
    reviewer_group_id = fields.Many2one(
        comodel_name="res.groups",
        compute="_compute_definition_data",
        store=True,
    )
    sequence = fields.Integer()
    has_comment = fields.Boolean(
        compute="_compute_definition_data",
        store=True,
    )
    approve_sequence = fields.Boolean(
        compute="_compute_definition_data",
        store=True,
    )

    @api.depends(
        "definition_id.name",
        "definition_id.review_type",
        "definition_id.reviewer_id",
        "definition_id.reviewer_group_id",
        "definition_id.has_comment",
        "definition_id.approve_sequence",
    )
    def _compute_definition_data(self):
        for rec in self:
            rec.name = rec.definition_id.name
            rec.review_type = rec.definition_id.review_type
            rec.reviewer_id = rec.definition_id.reviewer_id
            rec.reviewer_group_id = rec.definition_id.reviewer_group_id
            rec.has_comment = rec.definition_id.has_comment
            rec.approve_sequence = rec.definition_id.approve_sequence
