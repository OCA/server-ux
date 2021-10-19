# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class ValidationForwardWizard(models.TransientModel):
    _name = "tier.validation.forward.wizard"
    _description = "Forward Wizard"

    res_model = fields.Char()
    res_id = fields.Integer()
    forward_reviewer_id = fields.Many2one(
        comodel_name="res.users",
        string="Next Reviewer",
        required=True,
    )
    forward_description = fields.Char()
    has_comment = fields.Boolean(string="Allow Comment", default=True)
    approve_sequence = fields.Boolean(
        string="Approve by sequence",
        default=True,
    )
    can_backward = fields.Boolean(
        string="Can ask for review", compute="_compute_can_backward"
    )
    backward = fields.Boolean(
        string="Ask for review",
        default=False,
        help="The forwarded tier is meant for reivew, once approved, it will be back.",
    )

    @api.depends("forward_reviewer_id")
    def _compute_can_backward(self):
        self.ensure_one()
        record = self.env[self.res_model].browse(self.res_id)
        self.can_backward = record.can_backward

    def _get_tier_review_data(self, rec, prev_review):
        data = {
            "model": rec._name,
            "res_id": rec.id,
            "sequence": round(prev_review.sequence + 0.1, 2),
            "requested_by": self.env.uid,
        }
        if self.backward:
            data.update(
                {
                    "origin_id": prev_review.id,
                }
            )
        return data

    def add_forward(self):
        """ Add extra step, with specific reviewer """
        self.ensure_one()
        rec = self.env[self.res_model].browse(self.res_id)
        prev_comment = self.env["comment.wizard"].browse(
            self._context.get("comment_id")
        )
        prev_comment.write(
            {"comment": _(">> %s") % self.forward_reviewer_id.display_name}
        )
        prev_reviews = prev_comment.add_comment()
        prev_review = prev_reviews.sorted("sequence")[-1:]  # Get max sequence
        review = self.env["tier.review"].create(
            self._get_tier_review_data(rec, prev_review)
        )
        # Because following fileds are readonly, we need to write after create
        review.write(
            {
                "name": self.forward_description,
                "review_type": "individual",
                "reviewer_id": self.forward_reviewer_id.id,
                "has_comment": self.has_comment,
                "approve_sequence": self.approve_sequence,
            }
        )
        rec.invalidate_cache()
        rec.review_ids._compute_can_review()
