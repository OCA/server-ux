# Copyright 2020 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class TierReview(models.Model):
    _inherit = "tier.review"

    @api.constrains("status")
    def _trigger_substate(self):
        states = self.filtered(
            lambda l: l.status == "approved"
        ).mapped("definition_id").mapped("approved_substate_id")
        states += self.filtered(
            lambda l: l.status == "rejected"
        ).mapped("definition_id").mapped("rejected_substate_id")
        if not states:
            return
        if len(states) > 1:
            raise UserError(_(
                "More than 1 substate from validated tiers. Please check "
                "your tier definitions and make sure no conflict on substate"))
        res_id = self.mapped("res_id")[0]
        model = self.mapped("model")[0]
        record = self.env[model].browse(res_id)
        record.write({"substate_id": states[0].id})
