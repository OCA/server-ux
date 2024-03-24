# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class AccessRequest(models.Model):
    _name = "res.groups.access.request"
    _inherit = "mail.thread"
    _description = "Group Access Request"
    _rec_name = "user_id"

    user_id = fields.Many2one(
        "res.users",
        string="User",
        required=True,
        readonly=True,
        default=lambda self: self.env.user,
    )
    validate_user_id = fields.Many2one("res.users", string="Validator")
    reason = fields.Text(string="Reason for Access", required=True)
    state = fields.Selection(
        [("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")],
        default="pending",
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
    )
    group_id = fields.Many2one(
        "res.groups", string="Request To Access This Group", required=True
    )

    def button_approve(self):
        if not self.user_has_groups("analytic.group_analytic_tags"):
            raise UserError(
                _(
                    "Sorry, you cannot grant groups permissions to a group you don't belong"
                )
            )

        self.validate_user_id = self.env.user
        self.user_id.write(
            {
                "groups_id": [
                    (4, self.group_id.id),
                ]
            }
        )
        self.write({"state": "approved"})

    def button_reject(self):
        self.write({"state": "rejected"})
