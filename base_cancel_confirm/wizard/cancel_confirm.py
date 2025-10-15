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

    def _get_dict_update(self):
        """Hooks this method to update value in docs"""
        dict_update = {"cancel_confirm": True}
        # Cancel Reason
        if self.has_cancel_reason in ["optional", "required"]:
            dict_update.update({"cancel_reason": self.cancel_reason})
        return dict_update

    def confirm_cancel(self):
        self.ensure_one()
        res_model = self.env.context.get("cancel_res_model")
        res_ids = self.env.context.get("cancel_res_ids")
        cancel_method = self.env.context.get("cancel_method")
        docs = self.env[res_model].browse(res_ids)
        dict_update = self._get_dict_update()
        docs.write(dict_update)
        res = getattr(docs, cancel_method)()
        return res
