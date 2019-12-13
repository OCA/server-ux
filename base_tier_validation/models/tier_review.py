# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TierReview(models.Model):
    _name = "tier.review"
    _description = "Tier Review"

    name = fields.Char(related="definition_id.name", readonly=True)
    status = fields.Selection(
        selection=[("pending", "Pending"),
                   ("rejected", "Rejected"),
                   ("approved", "Approved")],
        default="pending",
    )
    model = fields.Char(string='Related Document Model', index=True)
    res_id = fields.Integer(string='Related Document ID', index=True)
    definition_id = fields.Many2one(
        comodel_name="tier.definition",
    )
    review_type = fields.Selection(
        related="definition_id.review_type", readonly=True,
    )
    reviewer_id = fields.Many2one(
        related="definition_id.reviewer_id", readonly=True,
    )
    reviewer_group_id = fields.Many2one(
        related="definition_id.reviewer_group_id", readonly=True,
    )
    reviewer_ids = fields.Many2many(
        string="Reviewers", comodel_name="res.users",
        compute="_compute_reviewer_ids", store=True,
    )
    sequence = fields.Integer(string="Tier")
    done_by = fields.Many2one(
        comodel_name="res.users",
    )
    requested_by = fields.Many2one(
        comodel_name="res.users",
    )
    reviewed_date = fields.Datetime(string='Validation Date')
    can_review = fields.Boolean()
    has_comment = fields.Boolean(
        related='definition_id.has_comment',
        readonly=True,
    )
    comment = fields.Char(
        string='Comments',
    )
    approve_sequence = fields.Boolean(
        related='definition_id.approve_sequence',
        readonly=True,
    )

    @api.model
    def _get_reviewer_fields(self):
        return ['reviewer_id', 'reviewer_group_id', 'reviewer_group_id.users']

    @api.multi
    @api.depends(lambda self: self._get_reviewer_fields())
    def _compute_reviewer_ids(self):
        for rec in self:
            rec.reviewer_ids = rec._get_reviewers()

    def _get_reviewers(self):
        return self.reviewer_id + self.reviewer_group_id.users
