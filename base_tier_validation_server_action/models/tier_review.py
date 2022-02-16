# Copyright 2020 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class TierReview(models.Model):
    _inherit = "tier.review"

    def write(self, vals):
        res = super().write(vals)
        if vals.get("status") == "approved":
            for rec in self:
                server_action = rec.definition_id.server_action_id
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
        return res
