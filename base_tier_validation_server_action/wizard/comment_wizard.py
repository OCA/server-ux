# Copyright 2022 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class CommentWizard(models.TransientModel):
    _inherit = "comment.wizard"

    def add_comment(self):
        """ For case reject only """
        res = super().add_comment()
        validate_reject = self._context.get("default_validate_reject")
        if validate_reject == "reject":
            review = self.review_ids[-1]
            reject_server_action = review.definition_id.rejected_server_action_id
            server_action_tier = self.env.context.get("server_action_tier")
            # Don't allow reentrant server action as it will lead to
            # recursive behaviour
            if reject_server_action and (
                not server_action_tier or server_action_tier != reject_server_action.id
            ):
                reject_server_action.with_context(
                    server_action_tier=reject_server_action.id,
                    active_model=review.model,
                    active_id=review.res_id,
                ).sudo().run()
        return res
