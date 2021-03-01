# Copyright 2020 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class BaseRevisionTester(models.Model):
    _name = "base.revision.tester"
    _description = "Base Revision Tester"
    _inherit = ["base.revision"]

    name = fields.Char(required=True)
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("cancel", "Cancel"),
        ],
        default="draft",
    )
    current_revision_id = fields.Many2one(
        comodel_name="base.revision.tester",
    )
    old_revision_ids = fields.One2many(
        comodel_name="base.revision.tester",
    )

    def action_confirm(self):
        self.write({"state": "confirmed"})

    def action_cancel(self):
        self.write({"state": "cancel"})
