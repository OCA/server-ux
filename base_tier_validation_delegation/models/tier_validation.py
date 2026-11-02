# Copyright 2026 360ERP (<https://www.360erp.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import logging

from odoo import models
from odoo.fields import Command

_logger = logging.getLogger(__name__)


class TierValidation(models.AbstractModel):
    _inherit = "tier.validation"

    def _find_review_for_delegate(self):
        """
        Finds a pending review where the current user is a delegate for one of
        the original reviewers.
        :return: A tuple of (tier.review, res.users) for the review and the
                 original delegator, or empty recordsets if not found.
        """
        self.ensure_one()
        user = self.env.user
        for review in self.review_ids.filtered(lambda r: r.status == "pending"):
            for original_reviewer in review._get_original_reviewers():
                if original_reviewer._get_final_validation_replacer() == user:
                    return review, original_reviewer
        return self.env["tier.review"], self.env["res.users"]

    def _execute_as_delegate(self, action):
        """
        Helper to perform an action (validate or reject) on behalf of a delegator.
        It temporarily adds the current user to the reviewers list to pass
        the base method's security checks.
        :param action: string, either 'validate' or 'reject'
        :return: A tuple containing (result_of_action, delegator_user, review)
        """
        review, delegator = self._find_review_for_delegate()
        if not review:
            return None, self.env["res.users"], self.env["tier.review"]

        _logger.debug(
            "DELEGATION [%s]: User '%s' is a delegate for review %s.",
            action,
            self.env.user.login,
            review.id,
        )
        # Temporarily add the delegate to pass base security checks
        review.sudo().reviewer_ids = [Command.link(self.env.user.id)]

        # Add a context key to prevent re-entrant calls
        ctx = self.with_context(in_delegation_flow=True).env.context

        if action == "validate":
            res = super(TierValidation, self.with_context(**ctx))._validate_tier(
                tiers=review
            )
        else:
            res = super(TierValidation, self.with_context(**ctx))._rejected_tier(
                tiers=review
            )

        return res, delegator, review

    def _validate_tier(self, tiers=False):
        """
        Allows a delegate user to validate a tier.
        """
        self.ensure_one()
        # If we are already in the delegation flow, do not re-run the logic.
        if self.env.context.get("in_delegation_flow"):
            return super()._validate_tier(tiers=tiers)

        # If user is a direct reviewer, use the standard method.
        if self.review_ids.filtered(
            lambda r: self.env.user in r.reviewer_ids and r.status == "pending"
        ):
            return super()._validate_tier(tiers=tiers)

        # If not a direct reviewer, check if they are a delegate.
        res, _delegator, _review = self._execute_as_delegate("validate")
        if res is not None:
            return res

        # Fallback to the standard method (which will likely raise an error)
        return super()._validate_tier(tiers=tiers)

    def _rejected_tier(self, tiers=False):
        """
        Allows a delegate user to reject a tier. Advanced policies are
        handled in the 'policy' module.
        This method now returns context for inheriting modules.
        :return: A tuple of (result, delegator, rejected_review)
        """
        self.ensure_one()
        # If we are already in the delegation flow, do not re-run the logic.
        if self.env.context.get("in_delegation_flow"):
            res = super()._rejected_tier(tiers=tiers)
            return res, self.env["res.users"], self.env["tier.review"]

        user = self.env.user
        delegator_to_notify = self.env["res.users"]
        rejected_review = self.env["tier.review"]
        res = None

        # If user is a direct reviewer, use the standard method.
        if self.review_ids.filtered(
            lambda r: user in r.reviewer_ids and r.status == "pending"
        ):
            res = super()._rejected_tier(tiers=tiers)
            # Find the delegator if the current user is also a replacer for someone else
            delegator_to_notify = self.review_ids.delegated_by_ids.filtered(
                lambda u: u._get_final_validation_replacer() == user
            )
            rejected_review = tiers or self.review_ids.filtered(
                lambda r: r.status == "rejected"
            )
        else:
            # If not a direct reviewer, check if they are a delegate.
            res, delegator_to_notify, rejected_review = self._execute_as_delegate(
                "reject"
            )
            if res is None:
                # Fallback to the standard method if not a delegate
                res = super()._rejected_tier(tiers=tiers)

        # Return all context for other modules to use
        return res, delegator_to_notify, rejected_review
