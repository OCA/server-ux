# Copyright 2024 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class TierReview(models.Model):
    _inherit = "tier.review"

    review_on_update = fields.Boolean(
        related="definition_id.review_on_update", readonly=True
    )
    on_update_type = fields.Selection(
        related="definition_id.on_update_type", readonly=True
    )

    new_values = fields.Serialized(readonly=True)

    def cancel_my_on_update_review(self):
        self.ensure_one()
        if (
            self.status == "pending"
            and self.review_on_update
            and self.requested_by == self.env.user
        ):
            self.unlink()
        return True

    def apply_update_on_record(self):
        self.ensure_one()
        # check if other reviews are pending on the same fields
        # before applying the changes. Can be improved in the future
        # to allow a more complex workflow.
        if self.review_on_update:
            pending_reviews = self.search(
                [
                    ("status", "=", "pending"),
                    ("res_id", "=", self.res_id),
                    ("id", "!=", self.id),
                ]
            )
            if pending_reviews:
                return True
        return (
            self.env[self.model]
            .with_context(skip_on_update_check=True)
            .browse(self.res_id)
            .write(self.new_values)
        )
