# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class OverdueReminderWizard(models.AbstractModel):
    _name = "overdue.reminder.wizard"
    _description = "Reminder Overdue Wizard"

    partner_ids = fields.Many2many(comodel_name="res.partner")
    min_interval_days = fields.Integer(
        string="Minimum Delay Since Last Reminder",
        help="Odoo will not propose to send a reminder to a customer "
        "that already got a reminder for some of the same overdue invoices "
        "less than N days ago (N = Minimum Delay Since Last Reminder).",
    )
    reminder_type = fields.Selection(
        selection="_reminder_type_selection", string="Reminder Type"
    )
    mail_template_id = fields.Many2one(comodel_name="mail.template")
    attachment_letter = fields.Boolean(string="Attach letter to email")
    letter_report = fields.Many2one(comodel_name="ir.actions.report")
    company_id = fields.Many2one(comodel_name="res.company", string="Company",)
    create_activity = fields.Boolean(readonly=True)
    activity_summary = fields.Char(string="Summary")
    activity_note = fields.Html(string="Note")

    @api.model
    def _reminder_type_selection(self):
        return [("mail", _("E-mail")), ("letter", _("Letter"))]

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        model = self._context.get("active_model", False)
        reminder = self.env["reminder.definition"].search([("model_id", "=", model)])
        res.update(
            {
                "min_interval_days": reminder
                and reminder.overdue_reminder_min_interval_days
                or 0.0,
                "company_id": reminder
                and reminder.company_id.id
                or self.env.company.id,
                "reminder_type": reminder and reminder.reminder_type or False,
                "mail_template_id": reminder and reminder.mail_template_id.id or False,
                "attachment_letter": reminder and reminder.attachment_letter,
                "letter_report": reminder and reminder.letter_report.id or False,
                "create_activity": reminder and reminder.create_activity,
                "activity_summary": reminder and reminder.activity_summary,
                "activity_note": reminder and reminder.activity_note,
            }
        )
        return res
