# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class TierValidation(models.AbstractModel):
    _inherit = "tier.validation"

    can_forward = fields.Boolean(compute="_compute_can_forward")

    def _compute_can_forward(self):
        for rec in self:
            if not rec.can_review:
                rec.can_forward = False
                continue
            sequences = self._get_sequences_to_approve(self.env.user)
            reviews = rec.review_ids.filtered(lambda l: l.sequence in sequences)
            definitions = reviews.mapped("definition_id")
            rec.can_forward = True in definitions.mapped("has_forward")

    @api.model
    def _calc_reviews_validated(self, reviews):
        """Override for different validation policy."""
        if not reviews:
            return False
        return not any(
            [s not in ("approved", "forwarded") for s in reviews.mapped("status")]
        )

    def _get_forwarded_notification_subtype(self):
        return "base_tier_validation.mt_tier_validation_forwarded"

    def forward_tier(self):
        self.ensure_one()
        sequences = self._get_sequences_to_approve(self.env.user)
        reviews = self.review_ids.filtered(lambda l: l.sequence in sequences)
        ctx = self._add_comment("forward", reviews)["context"]
        comment = self.env["comment.wizard"].with_context(ctx).create({"comment": "/"})
        wizard = self.env.ref("base_tier_validation_forward.view_forward_wizard")
        return {
            "name": _("Forward"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "tier.validation.forward.wizard",
            "views": [(wizard.id, "form")],
            "view_id": wizard.id,
            "target": "new",
            "context": {
                "default_res_id": self.id,
                "default_res_model": self._name,
                "comment_id": comment.id,
            },
        }

    def _forward_tier(self, tiers=False):
        self.ensure_one()
        tier_reviews = tiers or self.review_ids
        user_reviews = tier_reviews.filtered(
            lambda r: r.status != "approved" and (self.env.user in r.reviewer_ids)
        )
        user_reviews.write(
            {
                "status": "forwarded",
                "done_by": self.env.user.id,
                "reviewed_date": fields.Datetime.now(),
            }
        )
        for review in user_reviews:
            rec = self.env[review.model].browse(review.res_id)
            rec._notify_forwarded_reviews()

    def _notify_forwarded_reviews(self):
        post = "message_post"
        if hasattr(self, post):
            # Notify state change
            getattr(self, post)(
                subtype_xmlid=self._get_forwarded_notification_subtype(),
                body=self._notify_forwarded_reviews_body(),
            )

    def _notify_forwarded_reviews_body(self):
        has_comment = self.review_ids.filtered(
            lambda r: (self.env.user in r.reviewer_ids) and r.comment
        )
        if has_comment:
            comment = has_comment.mapped("comment")[0]
            return _(
                "A review was forwarded from {} {}".format(self.env.user.name, comment)
            )
        return _("A review was forwarded by %s.") % (self.env.user.name)
