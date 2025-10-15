# Copyright 2025 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class CancelConfirm(models.TransientModel):
    _inherit = "cancel.confirm"

    cancel_reason_id = fields.Many2one(
        comodel_name="res.cancel.reason",
        string="Reason for cancellation",
    )
    cancel_res_model = fields.Char(
        default=lambda self: self.env.context.get("cancel_res_model")
    )

    @api.onchange("cancel_reason_id")
    def _onchange_cancel_reason_id(self):
        if self.cancel_reason_id:
            self.cancel_reason = self.cancel_reason_id.name
        else:
            self.cancel_reason = False

    def _get_dict_update(self):
        dict_update = super()._get_dict_update()
        # Cancel Reason ID
        if self.has_cancel_reason in ["optional", "required"]:
            dict_update.update({"cancel_reason_id": self.cancel_reason_id.id})
        return dict_update
