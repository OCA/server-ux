# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


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
    todo_by = fields.Char(compute="_compute_todo_by", store=True)
    done_by = fields.Many2one(
        comodel_name="res.users",
    )
    requested_by = fields.Many2one(
        comodel_name="res.users",
    )
    reviewed_date = fields.Datetime(string='Validation Date')
    can_review = fields.Boolean(
        compute='_compute_can_review',
        store=True,
        help="""Can review will be marked if the review is pending and the
        approve sequence has been achieved""",
    )
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

    @api.depends('definition_id.approve_sequence')
    def _compute_can_review(self):
        for record in self:
            record.can_review = record._can_review_value()

    def _can_review_value(self):
        if self.status != 'pending':
            return False
        if not self.approve_sequence:
            return True
        resource = self.env[self.model].browse(self.res_id)
        reviews = resource.review_ids.filtered(
            lambda r: r.status in ('pending', 'rejected'))
        if not reviews:
            return True
        sequence = reviews.mapped('sequence')
        sequence.sort()
        current_sequence = sequence[0]
        return self.sequence == current_sequence

    @api.model
    def _get_reviewer_fields(self):
        return ['reviewer_id', 'reviewer_group_id', 'reviewer_group_id.users']

    @api.multi
    @api.depends(lambda self: self._get_reviewer_fields())
    def _compute_reviewer_ids(self):
        for rec in self:
            rec.reviewer_ids = rec._get_reviewers()

    @api.depends("reviewer_ids")
    def _compute_todo_by(self):
        """ Show by group or by abbrev list of names """
        num_show = 3  # Max number of users to display
        for rec in self:
            todo_by = False
            if rec.reviewer_group_id:
                todo_by = _("Group %s") % rec.reviewer_group_id.name
            else:
                todo_by = ", ".join(rec.reviewer_ids[:num_show].mapped("display_name"))
                num_users = len(rec.reviewer_ids)
                if num_users > num_show:
                    todo_by = "{} (and {} more)".format(todo_by, num_users - num_show)
            rec.todo_by = todo_by

    def _get_reviewers(self):
        return self.reviewer_id + self.reviewer_group_id.users
