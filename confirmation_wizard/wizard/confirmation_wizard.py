# Copyright (C) 2024 Cetmix OÜ
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from ast import literal_eval

from odoo import _, api, fields, models


class ConfirmationWizard(models.TransientModel):
    _name = "confirmation.wizard"
    _description = "Confirmation Wizard"

    message = fields.Char(string="Confirm Message", required=True)

    res_ids = fields.Char()
    res_model = fields.Char()

    callback_method = fields.Char()
    callback_params = fields.Json()

    return_type = fields.Selection(
        [
            ("window_close", "Return Window Close Action"),
            ("method", "Return Method"),
        ],
        default="window_close",
        required=True,
    )

    @api.model
    def _prepare_action(self, title=None):
        """
        Prepare confirmation wizard
        :param title: wizard title
        """
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "confirmation_wizard.confirmation_wizard_action"
        )
        action.update(
            {
                "name": title or _("Confirmation"),
                "res_id": self.id,
                "context": self._context,
            }
        )
        return action

    @api.model
    def confirm_message(
        self, message, records, title=None, method=None, callback_params=None
    ) -> dict | None:
        """
        Confirm message with method return type

        context: hide_cancel = True to hide confirm button

        :param message: confirmation message
        :param records: record set
        :param title: wizard title
        :param method: triggered method
        :param callback_params: method arguments
        :return dict: ir actions act window dict
        """
        if self._context.get("skip_confirm_message"):
            return
        wizard = self.create(
            {
                "message": message,
                "res_ids": repr(records.ids),
                "return_type": "method",
                "res_model": records._name,
                "callback_method": method,
                "callback_params": callback_params or {},
            }
        )
        return wizard.with_context(skip_confirm_message=True)._prepare_action(title)

    @api.model
    def confirm_no_action_message(self, message, title=None) -> dict | None:
        """
        Confirm message with close window return type

        context: hide_cancel = True to hide confirm button

        :param message: confirmation message
        :param title: wizard title
        :return dict: ir actions act window dict
        """
        if self._context.get("skip_confirm_no_action_message"):
            return
        wizard = self.create(
            {
                "message": message,
                "return_type": "window_close",
            }
        )
        return wizard.with_context(skip_confirm_message=True)._prepare_action(title)

    def _confirm_window_close(self):
        """Action confirm for return type window close"""
        return {"type": "ir.actions.act_window_close"}

    def _confirm_method(self):
        """Action confirm for return type method"""
        res_ids = literal_eval(self.res_ids) if self.res_ids else []
        records = self.env[self.res_model].browse(res_ids)
        if not records.exists():
            raise models.UserError(
                _("Records (IDS: '%(ids)s') not found in model '%(model)s'.")
                % {"ids": self.res_ids, "model": self.res_model}
            )
        if not hasattr(records, self.callback_method):
            raise models.UserError(
                _("Method '%(callback_method)s' is not found on model '%(res_model)s'.")
                % {"callback_method": self.callback_method, "res_model": self.res_model}
            )
        params = self.callback_params or {}
        return getattr(records, self.callback_method)(**params)

    def action_confirm(self):
        """Action confirm wizard"""
        method = getattr(self, f"_confirm_{self.return_type}", None)
        return method()
