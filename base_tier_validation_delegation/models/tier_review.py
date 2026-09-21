# Copyright 2026 360ERP (<https://www.360erp.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import logging

from markupsafe import Markup

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class TierReview(models.Model):
    _inherit = "tier.review"

    delegated_by_ids = fields.Many2many(
        comodel_name="res.users",
        relation="tier_review_delegated_by_rel",
        column1="review_id",
        column2="user_id",
        string="Delegated By",
        compute="_compute_reviewer_ids",
        store=True,
        help="Original users who delegated this review to the current reviewers.",
    )

    def _get_original_reviewers(self):
        """
        Helper method to get the reviewers as defined on the tier definition,
        bypassing any delegation logic from this module's override of `_get_reviewers`.
        """
        self.ensure_one()
        return self.with_context(skip_delegation=True)._get_reviewers()

    @api.depends(lambda self: self._get_reviewer_fields())
    def _compute_reviewer_ids(self):
        """
        Computes the final reviewers after applying delegation logic and also
        populates `delegated_by_ids` with any users whose reviews were reassigned.
        """
        old_reviewers_map = {rec.id: rec.reviewer_ids for rec in self}
        res = super()._compute_reviewer_ids()
        for rec in self:
            original_reviewers = rec._get_original_reviewers()
            final_reviewers = rec.reviewer_ids
            # The difference between original and final reviewers are the delegators
            delegators = original_reviewers - final_reviewers
            rec.delegated_by_ids = delegators

            # Post chatter message on change
            old_reviewers = old_reviewers_map.get(rec.id)
            if old_reviewers is not None and old_reviewers != final_reviewers:
                added = final_reviewers - old_reviewers
                removed = old_reviewers - final_reviewers
                if added and removed:
                    record = self.env[rec.model].browse(rec.res_id)
                    if record:
                        from_names = ", ".join(removed.mapped("name"))
                        to_names = ", ".join(added.mapped("name"))
                        body = Markup(
                            self.env._(
                                f"Review task delegated from <strong>{from_names}"
                                f"</strong> to <strong>{to_names}</strong>."
                            )
                        )
                        record.message_post(body=body)
        return res

    def _get_reviewers(self):
        """
        Overrides the base method to apply delegation logic. It gets the
        original reviewers and then substitutes anyone who is on holiday with
        their designated replacer.
        """
        original_reviewers = (
            super(TierReview, self.sudo())._get_reviewers().with_env(self.env)
        )
        if self.env.context.get("skip_delegation"):
            return original_reviewers

        final_reviewers = self.env["res.users"]
        for user in original_reviewers:
            final_replacer = user._get_final_validation_replacer()
            if user != final_replacer:
                _logger.debug(
                    "Review ID %s: User '%s' delegated to '%s'.",
                    self.id,
                    user.login,
                    final_replacer.login,
                )
            final_reviewers |= final_replacer
        # Return a unique set of reviewers
        return final_reviewers

    @api.model
    def _recompute_reviews_for_users(self, users):
        """
        Finds all pending reviews assigned to a given set of users (or delegated
        by them) and triggers a re-computation of their reviewers.
        """
        if not users:
            return

        # Find all pending reviews where any of the given users are either
        # a current reviewer OR the original delegator. This ensures we find
        # reviews even after they have been delegated.
        domain = [
            ("status", "in", ("pending", "waiting")),
            "|",
            ("reviewer_ids", "in", users.ids),
            ("delegated_by_ids", "in", users.ids),
        ]
        affected_reviews = self.search(domain)

        if affected_reviews.exists():
            affected_reviews._compute_reviewer_ids()
