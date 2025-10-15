# Copyright 2025 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class BaseCancelConfirm(models.AbstractModel):
    _inherit = "base.cancel.confirm"

    cancel_reason_id = fields.Many2one(
        comodel_name="res.cancel.reason",
        string="Cancel Reason Selection",
        index=True,
    )

    def _get_value_clear_cancel(self):
        vals_cancel = super()._get_value_clear_cancel()
        vals_cancel["cancel_reason_id"] = False
        return vals_cancel
