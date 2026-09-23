# Copyright 2022 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ReadAnnouncementWizard(models.TransientModel):
    _name = "read.announcement.wizard"
    _description = "Show altogether users who read and users who didn't"
    _order = "date desc"

    date = fields.Datetime(string="Read Date")
    user_id = fields.Many2one(comodel_name="res.users")
    announcement_id = fields.Many2one(comodel_name="announcement")
    read_state = fields.Selection(selection=[("read", "Read"), ("unread", "Unread")])
