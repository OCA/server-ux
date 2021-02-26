# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CancelConfirmTester(models.Model):
    _name = "cancel.confirm.tester"
    _description = "Cancel Confirm Tester"
    _inherit = ["base.cancel.confirm"]

    _has_cancel_reason = "optional"

    name = fields.Char()
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("cancel", "Cancel"),
        ],
        default="draft",
    )

    def action_confirm(self):
        self.write({"state": "confirmed"})

    def action_cancel(self):
        if not self.filtered("cancel_confirm"):
            return self.open_cancel_confirm_wizard()
        self.write({"state": "cancel"})

    def action_draft(self):
        self.clear_cancel_confirm_data()
        self.write({"state": "draft"})
