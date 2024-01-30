# Copyright 2020 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class TierReview(models.Model):
    _inherit = "tier.review"

    def _run_server_action(self):
        """
        Execute selected server action based on the status of the review
        while checking in the context if it's already done to avoid possible recursion
        """
        for rec in self.filtered(
            lambda review: not review.record_id.tier_validation_before_write
            and review.status in ["approved", "rejected"]
        ):
            server_action = False
            if rec.status == "approved":
                server_action = rec.definition_id.server_action_id
            if rec.status == "rejected":
                server_action = rec.definition_id.rejected_server_action_id
            server_action_tier = self.env.context.get("server_action_tier")
            # Don't allow reentrant server action as it will lead to
            # recursive behaviour
            if server_action and (
                not server_action_tier or server_action_tier != server_action.id
            ):
                server_action.with_context(
                    server_action_tier=server_action.id,
                    active_model=rec.model,
                    active_id=rec.res_id,
                ).sudo().run()

    def _post_process(self):
        self._run_server_action()

    def write(self, vals):
        res = super().write(vals)
        if vals.get("status") in ["approved", "rejected"]:
            self._post_process()
        return res
