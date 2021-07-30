# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ReminderDefinition(models.Model):
    _name = "reminder.definition"
    _description = "Reminder Definition"

    @api.model
    def _get_reminder_validation_model_names(self):
        res = []
        return res

    name = fields.Char(
        string="Description",
        required=True,
    )
    model_id = fields.Many2one(
        comodel_name="ir.model",
        string="Referenced Model",
        domain=lambda self: [
            ("model", "in", self._get_reminder_validation_model_names())
        ],
    )
    model = fields.Char(related="model_id.model", index=True, store=True)
    overdue_reminder_min_interval_days = fields.Integer(
        string="Minimum Interval", default=5
    )
    reminder_type = fields.Selection(
        selection="_reminder_type_selection",
        default="mail",
        string="Reminder",
        required=True,
    )
    mail_template_id = fields.Many2one(
        comodel_name="mail.template",
        compute="_compute_mail_template",
        readonly=False,
        store=True,
    )
    letter_report = fields.Many2one(comodel_name="ir.actions.report")
    attachment_letter = fields.Boolean(
        default=False,
        string="Attach Letter",
        help="Attach Letter to Overdue Reminder E-mails",
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    create_activity = fields.Boolean(
        help="If set, system will be notified reminder next time.",
    )
    activity_summary = fields.Char(string="Summary")
    activity_note = fields.Html(string="Note")

    @api.constrains("model_id")
    def _check_model_uniq(self):
        for rec in self:
            remind_id = self.search([("model_id", "=", rec.model_id.id)])
            if len(remind_id) > 1:
                raise UserError(_("You can configued model one by one only."))

    @api.depends("model_id")
    def _compute_mail_template(self):
        return True

    @api.model
    def _reminder_type_selection(self):
        return [("mail", _("E-mail")), ("letter", _("Letter"))]
