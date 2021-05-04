# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class OverdueReminderTester(models.Model):
    _name = "overdue.reminder.tester"
    _description = "Overdue Reminder Tester"
    _inherit = ["overdue.reminder.abstract"]


class OverdueReminderWizardTester(models.TransientModel):
    _name = "overdue.reminder.wizard.tester"
    _description = "Overdue Reminder Wizard Tester"
    _inherit = "overdue.reminder.wizard"
