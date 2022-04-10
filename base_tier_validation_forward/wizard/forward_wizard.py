# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, fields, models


class ValidationForwardWizard(models.TransientModel):
    _name = "tier.validation.forward.wizard"
    _description = "Forward Wizard"

    res_model = fields.Char()
    res_id = fields.Integer()
    forward_reviewer_id = fields.Many2one(
        comodel_name="res.users", string="Next Reviewer", required=True,
    )
    forward_description = fields.Char()
    has_comment = fields.Boolean(string="Allow Comment", default=True)
    approve_sequence = fields.Boolean(string="Approve by sequence", default=True,)

    def _prepare_tier_review_data(self):
        rec = self.env[self.res_model].browse(self.res_id)
        prev_comment = self.env["comment.wizard"].browse(
            self._context.get("comment_id")
        )
        prev_comment.write(
            {"comment": _(">> %s") % self.forward_reviewer_id.display_name}
        )
        prev_reviews = prev_comment.add_comment()
        return {
            "name": self.forward_description,
            "model": rec._name,
            "res_id": rec.id,
            "sequence": round(max(prev_reviews.mapped("sequence")) + 0.1, 2),
            "requested_by": self.env.uid,
            "review_type": "individual",
            "reviewer_id": self.forward_reviewer_id.id,
            "has_comment": self.has_comment,
            "approve_sequence": self.approve_sequence,
        }

    def add_forward(self):
        """ Add extra step, with specific reviewer """
        rec = self.env[self.res_model].browse(self.res_id)
        self.ensure_one()
        self.env["tier.review"].create(self._prepare_tier_review_data())
        rec.invalidate_cache()
        rec.review_ids._compute_can_review()
