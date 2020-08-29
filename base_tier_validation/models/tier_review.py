# Copyright 2017-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TierReview(models.Model):
    _name = "tier.review"
    _description = "Tier Review"
    _order = "sequence"

    name = fields.Char(compute="_compute_definition_data", store=True, readonly=False)
    status = fields.Selection(
        selection=[
            ("pending", "Pending"),
            ("rejected", "Rejected"),
            ("approved", "Approved"),
            ("escalated", "Escalated"),
        ],
        default="pending",
    )
    model = fields.Char(string="Related Document Model", index=True)
    res_id = fields.Integer(string="Related Document ID", index=True)
    definition_id = fields.Many2one(comodel_name="tier.definition")
    review_type = fields.Selection(
        selection=[
            ("individual", "Specific user"),
            ("group", "Any user in a specific group."),
        ],
        compute="_compute_definition_data",
        store=True,
        readonly=False,
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
    reviewer_ids = fields.Many2many(
        string="Reviewers",
        comodel_name="res.users",
        compute="_compute_reviewer_ids",
        store=True,
    )
    sequence = fields.Float(string="Tier")
    done_by = fields.Many2one(comodel_name="res.users")
    requested_by = fields.Many2one(comodel_name="res.users")
    reviewed_date = fields.Datetime(string="Validation Date")
    has_comment = fields.Boolean(
        compute="_compute_definition_data", store=True, readonly=False
    )
    comment = fields.Char(string="Comments")
    can_review = fields.Boolean(
        compute="_compute_can_review",
        store=True,
        help="""Can review will be marked if the review is pending and the
        approve sequence has been achieved""",
    )
    approve_sequence = fields.Boolean(
        compute="_compute_definition_data", store=True, readonly=False
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

    @api.depends("definition_id.approve_sequence")
    def _compute_can_review(self):
        for record in self.sorted("sequence"):
            record.can_review = record._can_review_value()

    def _can_review_value(self):
        if self.status != "pending":
            return False
        if not self.approve_sequence:
            return True
        resource = self.env[self.model].browse(self.res_id)
        resource.invalidate_cache()
        reviews = resource.review_ids.filtered(lambda r: r.status == "pending")
        if not reviews:
            return False
        sequence = min(reviews.mapped("sequence"))
        return self.sequence == sequence

    @api.model
    def _get_reviewer_fields(self):
        return ["reviewer_id", "reviewer_group_id", "reviewer_group_id.users"]

    @api.depends(lambda self: self._get_reviewer_fields())
    def _compute_reviewer_ids(self):
        for rec in self:
            rec.reviewer_ids = rec._get_reviewers()

    def _get_reviewers(self):
        return self.reviewer_id + self.reviewer_group_id.users
