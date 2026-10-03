# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


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

    def add_forward(self):
        """Add extra step, with specific reviewer"""
        self.ensure_one()
        rec = self.env[self.res_model].browse(self.res_id)
        # Subscribe the forward target as a follower so they receive
        # email notifications about the forwarded review.
        if hasattr(rec, "message_subscribe"):
            fwd_subtype = self.env.ref(
                "base_tier_validation_forward.mt_tier_validation_forwarded",
                raise_if_not_found=False,
            )
            rec.message_subscribe(
                partner_ids=self.forward_reviewer_id.partner_id.ids,
                subtype_ids=fwd_subtype.ids if fwd_subtype else [],
            )
        prev_comment = self.env["comment.wizard"].browse(
            self._context.get("comment_id")
        )
        prev_comment.write(
            {
                "comment": self.env._(
                    ">> %(reviewer)s", reviewer=self.forward_reviewer_id.display_name
                )
            }
        )
        prev_comment.with_context(
            tier_validation_defer_compute_can_review=True
        ).add_comment()
        prev_reviews = prev_comment.review_ids
        review = (
            self.env["tier.review"]
            .with_context(tier_validation_defer_compute_can_review=True)
            .create(
                {
                    "model": rec._name,
                    "res_id": rec.id,
                    "sequence": max(prev_reviews.mapped("sequence")),
                    "requested_by": self.env.uid,
                }
            )
        )
        # Because following fields are readonly, we need to write after create
        review.write(
            {
                "name": self.forward_description,
                "review_type": "individual",
                "reviewer_id": self.forward_reviewer_id.id,
                "has_comment": self.has_comment,
                "approve_sequence": self.approve_sequence,
            }
        )
        rec.invalidate_recordset()
        rec.review_ids._compute_can_review()
