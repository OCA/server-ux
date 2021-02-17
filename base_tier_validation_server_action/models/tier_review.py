# Copyright 2020 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class TierReview(models.Model):
    _inherit = "tier.review"

    @api.constrains("status")
    def _trigger_server_action(self):
        for rec in self.filtered(lambda l: l.status in ["approved", "rejected"]):
            server_action = False
            if rec.status == "approved":
                server_action = rec.definition_id.server_action_id
            if rec.status == "rejected":
                server_action = rec.definition_id.rejected_server_action_id
            if server_action:
                ctx = {"active_model": rec.model, "active_id": rec.res_id}
                server_action.with_context(ctx).run()
