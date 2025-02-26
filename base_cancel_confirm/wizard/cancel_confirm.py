# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class CancelConfirm(models.TransientModel):
    _name = "cancel.confirm"
    _description = "Cancel Confirm"

    cancel_reason = fields.Text()
    has_cancel_reason = fields.Selection(
        selection=[
            ("no", "None"),
            ("optional", "Optional"),
            ("required", "Required"),
        ],
        default="no",
        required=True,
    )

    def confirm_cancel(self):
        self.ensure_one()
        res_model = self._context.get("cancel_res_model")
        res_ids = self._context.get("cancel_res_ids")
        cancel_method = self._context.get("cancel_method")
        docs = self.env[res_model].browse(res_ids)
        docs.write({"cancel_confirm": True})
        # Cancel Reason
        if self.has_cancel_reason in ["optional", "required"]:
            docs.write({"cancel_reason": self.cancel_reason})
        res = getattr(docs, cancel_method)()
        return res
