# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class OverdueReminder(models.AbstractModel):
    _name = "overdue.reminder.abstract"
    _description = "Overdue Reminder Abstract"
    _order = "id desc"

    name = fields.Char(required=True, default="/", readonly=True, copy=False)
    partner_id = fields.Many2one(comodel_name="res.partner", required=True)
    partner_email = fields.Char(related="partner_id.email", readonly=True)
    partner_phone = fields.Char(related="partner_id.phone", readonly=True)
    partner_mobile = fields.Char(related="partner_id.mobile", readonly=True)
    commercial_partner_id = fields.Many2one(
        comodel_name="res.partner", readonly=True, required=True
    )
    user_id = fields.Many2one(comodel_name="res.users", readonly=True)
    date = fields.Date(default=fields.Date.context_today, readonly=True)
    reminder_type = fields.Selection(
        selection="_reminder_type_selection",
        default="mail",
        string="Reminder Type",
        required=True,
    )
    mail_count = fields.Integer(compute="_compute_mail_count", store=True)
    mail_template_id = fields.Many2one(comodel_name="mail.template", readonly=True)
    mail_subject = fields.Char(string="Subject")
    mail_body = fields.Html()
    attachment_letter = fields.Boolean(
        string="Attach Letter",
        readonly=True,
        help="Attach Letter to Overdue Reminder E-mails",
    )
    letter_report = fields.Many2one(comodel_name="ir.actions.report", readonly=True)
    create_activity = fields.Boolean()
    activity_type_id = fields.Many2one(
        comodel_name="mail.activity.type", string="Activity"
    )
    activity_summary = fields.Char(string="Summary")
    activity_scheduled_date = fields.Date(string="Scheduled Date")
    activity_note = fields.Html(string="Note")
    activity_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Assigned to",
        default=lambda self: self.env.user,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        readonly=True,
        required=True,
        default=lambda self: self.env.company,
    )
    state = fields.Selection(
        [("draft", "Draft"), ("cancel", "Cancelled"), ("done", "Done")],
        default="draft",
        readonly=True,
    )

    def _domain_search_mail(self):
        domain = [("model", "=", self._name), ("res_id", "in", self.ids)]
        return domain

    @api.depends("state")
    def _compute_mail_count(self):
        domain = self._domain_search_mail()
        mail_data = self.env["mail.mail"].read_group(domain, ["res_id"], ["res_id"])
        mail = {data["res_id"]: data["res_id_count"] for data in mail_data}
        for rec in self:
            rec.mail_count = mail.get(rec.id, 0)

    @api.model
    def _reminder_type_selection(self):
        return [("mail", _("E-mail")), ("letter", _("Letter"))]

    @api.model
    def _hook_mail_template(self, action, vals, mail_subject=False, mail_body=False):
        """ Hook create mail subject and description"""
        return mail_subject, mail_body

    @api.model
    def create(self, vals):
        action = super().create(vals)
        mail_subject, mail_body = self._hook_mail_template(action, vals)
        action.write({"mail_subject": mail_subject, "mail_body": mail_body})
        return action

    def check_warnings(self):
        """ Hooks function"""
        return True

    def print_letter(self):
        self.check_warnings()
        action = self.letter_report.with_context(
            {"discard_logo_check": True}
        ).report_action(self)
        return action
