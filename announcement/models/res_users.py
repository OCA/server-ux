# Copyright 2022 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    pendant_announcement_ids = fields.Many2many(
        comodel_name="announcement", relation="pendant_announcement_user_rel",
    )
    read_announcement_ids = fields.Many2many(
        comodel_name="announcement", relation="read_announcement_user_rel",
    )
    popup_announcements = fields.Boolean()

    @api.model
    def announcement_user_count(self):
        """The js widget gathers the announcements from this method"""
        now = fields.Datetime.now()
        group_announcements = self.env["announcement"].search_read(
            [
                ("announcement_type", "=", "user_group"),
                "|",
                ("notification_date", "<=", now),
                ("notification_date", "=", False),
                "|",
                ("notification_expiry_date", ">=", now),
                ("notification_expiry_date", "=", False),
                ("id", "not in", self.env.user.read_announcement_ids.ids),
            ],
            ["user_group_ids"],
        )
        announcements = self.env["announcement"].browse(
            {
                x["id"]
                for x in group_announcements
                if any(
                    [g for g in x["user_group_ids"] if g in self.env.user.groups_id.ids]
                )
            }
        )
        announcements |= self.env.user.pendant_announcement_ids.filtered(
            lambda x: (not x.notification_date or x.notification_date <= now)
            and (not x.notification_expiry_date or x.notification_expiry_date >= now)
        ).sorted(lambda k: k.sequence)
        return announcements.read()

    @api.model
    def mark_announcement_as_read(self, announcement_id):
        """Used as a controller for the widget"""
        self.env.user.popup_announcements = False
        announcement = self.env["announcement"].browse(int(announcement_id))
        self.env.user.pendant_announcement_ids -= announcement
        self.env.user.read_announcement_ids += announcement
        self.env["announcement.log"].create({"announcement_id": announcement.id})

    @api.model
    def _update_last_login(self):
        """When the user logs in and has pendant announcements they'll be popped up"""
        self.env.user.popup_announcements = bool(self.env.user.announcement_user_count)
        return super()._update_last_login()
