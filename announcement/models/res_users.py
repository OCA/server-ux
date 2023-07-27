# Copyright 2022 Tecnativa - David Vidal
# Copyright 2022 Tecnativa - Pilar Vargas
# Copyright 2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from markupsafe import Markup

from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    unread_announcement_ids = fields.Many2many(
        comodel_name="announcement",
        relation="unread_announcement_user_rel",
    )
    read_announcement_ids = fields.Many2many(
        comodel_name="announcement",
        relation="read_announcement_user_rel",
    )

    @api.model
    def announcement_user_count(self):
        """The js widget gathers the announcements from this method"""
        # It would be better to rely on record rules, but then announcement managers
        # would see every announcement, which would be annoying.
        group_announcements = self.env["announcement"].search_read(
            [
                ("announcement_type", "=", "user_group"),
                ("in_date", "=", True),
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
        # Unread announcements are directly linked to the user. Normally, only a
        # handful of records will be evaluated at best.
        announcements |= self.env.user.unread_announcement_ids.filtered("in_date")
        return [
            {
                "id": announcement.id,
                "name": announcement.name,
                "content": self._add_attachment_links(announcement),
            }
            for announcement in announcements.sorted(lambda k: k.sequence)
        ]

    def _add_attachment_links(self, announcement):
        """In case the announcement has attachments, show the list below the
        modal content"""
        content = announcement.content
        attachment_links = ""
        if announcement.attachment_ids:
            attachment_links += "<div class='list-group'>"
            for attachment in announcement.attachment_ids:
                attachment_url = "/web/content/%s?download=false" % attachment.id
                attachment_link = """<a href="%s" class="list-group-item list-group-item-action"
                    target="_blank"><i class="fa fa-download" /> %s</a>""" % (
                    attachment_url,
                    attachment.name,
                )
                attachment_links += attachment_link
            attachment_links += "</div>"
        if attachment_links:
            content += Markup("<br/>") + Markup(attachment_links)
        return content

    @api.model
    def mark_announcement_as_read(self, announcement_id):
        """Used as a controller for the widget"""
        announcement = self.env["announcement"].browse(int(announcement_id))
        self.env.user.unread_announcement_ids -= announcement
        # Log only the first time. Users with the announcement in multiple windows would
        # log multiple reads. We're only interested in the first one.
        if announcement not in self.env.user.read_announcement_ids:
            self.env.user.read_announcement_ids += announcement
            self.env["announcement.log"].create({"announcement_id": announcement.id})
