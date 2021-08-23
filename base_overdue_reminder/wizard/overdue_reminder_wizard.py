# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models


class OverdueReminderWizard(models.AbstractModel):
    _name = "overdue.reminder.wizard"
    _description = "Reminder Overdue Wizard"

    partner_ids = fields.Many2many(comodel_name="res.partner")
    reminder_number = fields.Integer(
        string="Reminder Every (days)",
    )
    reminder_next_time = fields.Date(
        string="Next Reminder",
        compute="_compute_reminder_next_time",
        store=True,
        readonly=False,
    )
    reminder_type = fields.Selection(
        selection="_reminder_type_selection", string="Reminder Type"
    )
    mail_template_id = fields.Many2one(comodel_name="mail.template")
    attachment_letter = fields.Boolean(string="Attach letter to email")
    letter_report = fields.Many2one(comodel_name="ir.actions.report")
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
    )
    create_activity = fields.Boolean(readonly=True)
    activity_type_id = fields.Many2one(
        comodel_name="mail.activity.type", string="Activity"
    )
    activity_summary = fields.Char(string="Summary")
    activity_note = fields.Html(string="Note")

    @api.depends("reminder_number")
    def _compute_reminder_next_time(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.reminder_next_time = today + relativedelta(days=rec.reminder_number)

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
                "reminder_number": reminder and reminder.reminder_number or 0,
                "company_id": reminder
                and reminder.company_id.id
                or self.env.company.id,
                "reminder_type": reminder and reminder.reminder_type or False,
                "mail_template_id": reminder and reminder.mail_template_id.id or False,
                "attachment_letter": reminder and reminder.attachment_letter,
                "letter_report": reminder and reminder.letter_report.id or False,
                "create_activity": reminder and reminder.create_activity,
                "activity_type_id": reminder and reminder.activity_type_id.id or False,
                "activity_summary": reminder and reminder.activity_summary,
                "activity_note": reminder and reminder.activity_note,
            }
        )
        return res
