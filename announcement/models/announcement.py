# Copyright 2022 Tecnativa - David Vidal
# Copyright 2022 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class AnnouncementLog(models.Model):
    _name = "announcement.log"
    _description = "Log user reads"
    _order = "create_date desc"

    announcement_id = fields.Many2one(comodel_name="announcement")


class Announcement(models.Model):
    _name = "announcement"
    _description = "User announcements"
    _order = "notification_date, sequence asc, id"

    active = fields.Boolean(copy=False)
    sequence = fields.Integer()
    name = fields.Char(string="Title", required=True)
    content = fields.Html()
    tag_ids = fields.Many2many(
        comodel_name="announcement.tag",
        column1="announcement_id",
        column2="tag_id",
        string="Tags",
    )
    is_general_announcement = fields.Boolean("General Announcement")
    attachment_ids = fields.Many2many(
        comodel_name="ir.attachment",
        string="Attachments",
        help="You can attach the copy of your Letter",
    )
    announcement_type = fields.Selection(
        selection=[
            ("specific_users", "Specific users"),
            ("user_group", "User groups"),
        ],
        default="specific_users",
        required=True,
    )
    specific_user_ids = fields.Many2many(
        comodel_name="res.users",
        context={"active_test": False},
        domain=[("share", "=", False)],
        inverse="_inverse_specific_user_ids",
    )
    user_group_ids = fields.Many2many(
        comodel_name="res.groups",
        compute="_compute_user_group_ids",
        store=True,
        readonly=False,
    )
    allowed_user_ids = fields.Many2many(
        comodel_name="res.users",
        relation="announcement_res_users_allowed_rel",
        compute="_compute_allowed_user_ids",
        compute_sudo=True,
        store=True,
    )
    allowed_users_count = fields.Integer(
        compute="_compute_allowed_user_ids",
        compute_sudo=True,
        store=True,
    )
    read_announcement_count = fields.Integer(
        compute="_compute_read_announcement_count",
        store=True,
    )
    notification_date = fields.Datetime()
    notification_expiry_date = fields.Datetime()
    notification_start_date = fields.Datetime(
        compute="_compute_notification_start_date",
        help="Technical field to display announcements in the calendar view",
    )
    notification_end_date = fields.Datetime(
        compute="_compute_notification_end_date",
        help="Technical field to display announcements in the calendar view",
    )
    color = fields.Integer(
        compute="_compute_color",
        help="Technical field to display items by color in the calendar",
    )
    in_date = fields.Boolean(
        compute="_compute_in_date", search="_search_in_date", compute_sudo=True
    )
    announcement_log_ids = fields.One2many(
        comodel_name="announcement.log",
        inverse_name="announcement_id",
    )

    def _inverse_specific_user_ids(self):
        """Used to set users unread announcements when they're set in the announcement
        itself"""
        for announcement in self:
            for user in announcement.specific_user_ids.filtered(
                lambda x: announcement
                not in (x.read_announcement_ids + x.unread_announcement_ids)
            ):
                user.unread_announcement_ids |= announcement

    @api.depends("specific_user_ids", "user_group_ids")
    def _compute_allowed_user_ids(self):
        self.allowed_user_ids = False
        self.allowed_users_count = False
        specific_user_announcements = self.filtered(
            lambda x: x.announcement_type == "specific_users"
        )
        for announcement in specific_user_announcements:
            announcement.allowed_user_ids = announcement.specific_user_ids
            announcement.allowed_users_count = len(announcement.specific_user_ids)
        for announcement in self - specific_user_announcements:
            announcement.allowed_user_ids = announcement.user_group_ids.users
            announcement.allowed_users_count = len(announcement.user_group_ids.users)

    @api.depends("is_general_announcement")
    def _compute_user_group_ids(self):
        for announcement in self:
            if announcement.is_general_announcement:
                announcement.announcement_type = "user_group"
                announcement.user_group_ids = self.env.ref("base.group_user")
            else:
                announcement.user_group_ids = False

    @api.depends("announcement_log_ids")
    def _compute_read_announcement_count(self):
        logs = self.env["announcement.log"].read_group(
            [("announcement_id", "in", self.ids)],
            ["announcement_id"],
            ["announcement_id"],
        )
        result = {
            data["announcement_id"][0]: (data["announcement_id_count"]) for data in logs
        }
        for announcement in self:
            announcement.read_announcement_count = result.get(announcement.id, 0)

    @api.depends("notification_date")
    def _compute_notification_start_date(self):
        """This is a technical field that we'll use so we're able to render
        announcements with no defined start date. Otherwise they don't show up"""
        for announcement in self:
            announcement.notification_start_date = (
                announcement.notification_date or announcement.create_date
            )

    @api.depends("notification_expiry_date", "notification_date")
    def _compute_notification_end_date(self):
        """This is a technical field that we'll use so we're able to render no end
        announcements in the calendar"""
        for announcement in self:
            announcement.notification_end_date = (
                announcement.notification_expiry_date
                # We don't want undefined end announment appearing forever in the
                # calendar just because one user didn't read them. So we just
                # show them in the date they start
                or announcement.notification_start_date
            )

    @api.depends("tag_ids")
    def _compute_color(self):
        """Get the first tag color if any. Used in the calendar"""
        self.color = False
        for announcement in self.filtered("tag_ids"):
            announcement.color = announcement.tag_ids[0].color

    def _compute_in_date(self):
        """The announcement is publishable according to date criterias"""
        self.in_date = False
        now = fields.Datetime.now()
        for record in self:
            date_passed = (
                not record.notification_date or record.notification_date <= now
            )
            date_unexpired = (
                not record.notification_expiry_date
                or record.notification_expiry_date >= now
            )
            record.in_date = date_passed and date_unexpired

    def _search_in_date(self, operator, value):
        """Used mainly for record rules as time module values will be cached"""
        now = fields.Datetime.now()
        return [
            "|",
            ("notification_date", "=", False),
            ("notification_date", "<=", now),
            "|",
            ("notification_expiry_date", "=", False),
            ("notification_expiry_date", ">=", now),
        ]

    def _process_attachments(self, vals):
        """Assign attachments owner (if not yet set) or create a copy of the added
        attachments for making sure that they are accessible to the users that read
        the announcement.
        """
        if self.env.context.get("bypass_attachment_process"):
            return
        for command in vals.get("attachment_ids", []):
            to_process = []
            if command[0] == 4:
                to_process.append(command[1])
            elif command[0] == 6:
                to_process += command[2]
            for attachment_id in to_process:
                attachment = self.env["ir.attachment"].browse(attachment_id)
                for record in self:
                    if not attachment.res_id:
                        attachment.res_id = record.id
                        attachment.res_model = record._name
                    else:
                        new_attachment = attachment.copy(
                            {"res_id": record.id, "res_model": record._name}
                        )
                        record.with_context(
                            bypass_attachment_process=True
                        ).attachment_ids = [(3, attachment_id), (4, new_attachment.id)]

    @api.model_create_multi
    def create(self, vals_list):
        """Adjust attachments for being accesible to receivers of the announcement."""
        records = super().create(vals_list)
        for vals in vals_list:
            records._process_attachments(vals)
        return records

    def write(self, vals):
        """Adjust attachments for being accesible to receivers of the announcement."""
        res = super().write(vals)
        self._process_attachments(vals)
        return res

    @api.onchange("announcement_type")
    def _onchange_announcement_type(self):
        """We want to reset the values on screen"""
        if self.announcement_type == "specific_users":
            self.user_group_ids = False
        elif self.announcement_type == "user_group":
            self.specific_user_ids = False

    def action_announcement_log(self):
        """See altogether read logs and unread users"""
        self.ensure_one()
        read_logs = self.env["announcement.log"].search(
            [("announcement_id", "in", self.ids)]
        )
        unread_users = self.allowed_user_ids.filtered(
            lambda x: x not in read_logs.create_uid
        )
        read_unread_log = self.env["read.announcement.wizard"].create(
            [
                {
                    "user_id": log.create_uid.id,
                    "date": log.create_date,
                    "announcement_id": self.id,
                    "read_state": "read",
                }
                for log in read_logs
            ]
        )
        read_unread_log += self.env["read.announcement.wizard"].create(
            [{"user_id": user.id, "read_state": "unread"} for user in unread_users]
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": "read.announcement.wizard",
            "views": [[False, "tree"]],
            "domain": [("id", "in", read_unread_log.ids)],
            "context": dict(self.env.context, create=False, group_by=["read_state"]),
            "name": _("Read Logs"),
        }
