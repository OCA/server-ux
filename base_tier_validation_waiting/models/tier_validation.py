# Copyright (c) 2022 brain-tec AG (https://braintec.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class TierValidation(models.AbstractModel):
    _inherit = "tier.validation"

    def _notify_review_available(self, tier_reviews):
        """method to notify when reaching pending"""
        subscribe = "message_subscribe"
        post = "message_post"
        if hasattr(self, post) and hasattr(self, subscribe):
            for rec in self.sudo():
                users_to_notify = tier_reviews.filtered(
                    lambda r: r.definition_id.notify_on_pending and r.res_id == rec.id
                ).mapped("reviewer_ids")
                # Subscribe reviewers and notify
                getattr(rec, subscribe)(
                    partner_ids=users_to_notify.mapped("partner_id").ids
                )
                getattr(rec, post)(
                    subtype_xmlid=self._get_requested_notification_subtype(),
                    body=rec._notify_requested_review_body(),
                )

    def _validate_tier_waiting_reviews(self, tiers=False):
        tier_reviews = tiers or self.review_ids
        waiting_reviews = tier_reviews.filtered(
            lambda r: r.status == "waiting"
            and (self.env.user in r.reviewer_ids)
            and r.approve_sequence_bypass
        )
        if waiting_reviews:
            waiting_reviews.write(
                {
                    "status": "approved",
                    "done_by": self.env.user.id,
                    "reviewed_date": fields.Datetime.now(),
                }
            )
            for review in waiting_reviews:
                rec = self.env[review.model].browse(review.res_id)
                rec._notify_accepted_reviews()

    def _validate_tier(self, tiers=False):
        """extend base tier validation method to allow bypass of waiting
        sequences as pending state is hardcoded"""
        self.ensure_one()
        self._validate_tier_waiting_reviews(tiers)
        res = super(TierValidation, self)._validate_tier(tiers)
        return res
