# Copyright (c) 2022 brain-tec AG (https://braintec.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools import config


class TierReview(models.Model):
    _inherit = "tier.review"

    def _default_status(self):
        if (
            not config["test_enable"]
            or config["test_enable"]
            and self.env.context.get("testing_base_tier_validation_waiting")
        ):
            return "waiting"
        else:
            return "pending"

    status = fields.Selection(
        selection_add=[("waiting", "Waiting")],
        default=_default_status,
        ondelete={"waiting": "set default"},
    )

    def _notify_pending_status(self, review_ids):
        """Method to call and reuse abstract notification method"""
        resource = self.env[self.model].browse(self.res_id)
        resource._notify_review_available(review_ids)

    @api.depends("definition_id.approve_sequence")
    def _compute_can_review(self):
        """inherit base module to push forward waiting reviews"""
        reviews = self.filtered(
            lambda rev: rev.status in ["waiting", "pending", "rejected"]
        )
        if reviews:
            # get minimum sequence of all to prevent jumps
            next_seq = min(reviews.mapped("sequence"))
            for record in reviews:
                # if not in waiting, nothing to do
                if record.status != "waiting":
                    continue
                # if approve by sequence, check sequence has been reached
                if record.approve_sequence:
                    if record.sequence == next_seq:
                        record.status = "pending"
                # if there is no approval sequence go directly to pending state
                elif not record.approve_sequence:
                    record.status = "pending"
                # notify if state has changed
                if record.status == "pending":
                    if record.definition_id.notify_on_pending:
                        record._notify_pending_status(record)
        return super(TierReview, self)._compute_can_review()
