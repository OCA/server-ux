# Copyright 2021 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class TierReview(models.Model):
    _inherit = "tier.review"

    @api.constrains("status")
    def _trigger_forwarded_server_action(self):
        for rec in self.filtered(lambda l: l.status == "forwarded"):
            server_action = rec.definition_id.forwarded_server_action_id
            if server_action:
                ctx = {"active_model": rec.model, "active_id": rec.res_id}
                server_action.with_context(ctx).run()
