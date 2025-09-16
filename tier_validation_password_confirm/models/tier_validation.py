# Copyright 2025 ForgeFlow S.L.

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class TierValidation(models.AbstractModel):
    _inherit = "tier.validation"

    require_password = fields.Boolean(compute="_compute_require_password")

    def _compute_require_password(self):
        for rec in self:
            require_password = rec.review_ids.filtered(
                lambda r: r.status == "pending" and (self.env.user in r.reviewer_ids)
            ).mapped("require_password")
            rec.require_password = True in require_password

    def validate_tier(self):
        self.ensure_one()
        sequences = self._get_sequences_to_approve(self.env.user)
        reviews = self.review_ids.filtered(
            lambda r: r.sequence in sequences or r.approve_sequence_bypass
        )
        if self.has_comment or self.require_password:
            user_reviews = reviews.filtered(
                lambda r: r.status == "pending" and (self.env.user in r.reviewer_ids)
            )
            return self._add_comment("validate", user_reviews)
        self._validate_tier(reviews)
        self._update_counter()

    def _add_comment(self, validate_reject, reviews):
        res = super()._add_comment(validate_reject, reviews)
        res["context"]["comment"] = self.has_comment
        res["context"]["require_password"] = self.require_password
        return res

    def _validate_tier(self, tiers=False):
        self.ensure_one()
        tier_reviews = tiers or self.review_ids
        user_reviews = tier_reviews.filtered(
            lambda r: r.status == "pending" and (self.env.user in r.reviewer_ids)
        )
        for review in user_reviews:
            if review.require_password and not review.password_confirmed:
                raise ValidationError(
                    _(
                        "You need to request a validation, because "
                        "the reviewer requires a password to validate."
                    )
                )
        return super()._validate_tier(tiers)
