# Copyright 2020 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class TierReview(models.Model):
    _inherit = "tier.review"

    def write(self, vals):
        res = super().write(vals)
        if vals.get("status") in ["approved", "rejected"]:
            for rec in self:
                server_action = False
                if rec.status == "approved":
                    server_action = rec.definition_id.server_action_id
                if rec.status == "rejected":
                    server_action = rec.definition_id.rejected_server_action_id
                if server_action:
                    server_action.with_context(
                        active_model=rec.model,
                        active_id=rec.res_id,
                    ).sudo().run()
        return res
