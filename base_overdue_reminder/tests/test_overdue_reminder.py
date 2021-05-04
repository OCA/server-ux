# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests import common

from .common import setup_test_model, teardown_test_model
from .overdue_reminder_tester import OverdueReminderTester, OverdueReminderWizardTester


@common.at_install(False)
@common.post_install(True)
class TestOverdueReminder(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        setup_test_model(cls.env, [OverdueReminderTester, OverdueReminderWizardTester])
        cls.test_model = cls.env[OverdueReminderTester._name]
        cls.partner_1 = cls.env.ref("base.res_partner_1")
        cls.report_test = cls.env.ref("base.report_ir_model_overview")
        cls.tester_model = cls.env["ir.model"].search(
            [("model", "=", "overdue.reminder.tester")]
        )
        # Access record:
        cls.env["ir.model.access"].create(
            {
                "name": "access.tester",
                "model_id": cls.tester_model.id,
                "perm_read": 1,
                "perm_write": 1,
                "perm_create": 1,
                "perm_unlink": 1,
            }
        )
        # Create users:
        group_ids = cls.env.ref("base.group_system").ids
        cls.test_user_1 = cls.env["res.users"].create(
            {"name": "John", "login": "test1", "groups_id": [(6, 0, group_ids)]}
        )
        cls.test_record = cls.test_model.create(
            {
                "commercial_partner_id": cls.partner_1.id,
                "partner_id": cls.partner_1.id,
                "reminder_type": "mail",
                "attachment_letter": True,
                "letter_report": cls.report_test.id,
            }
        )
        cls.reminder_definition = cls.env["reminder.definition"].create(
            {
                "model_id": False,
                "name": "Reminder Test",
                "reminder_type": "mail",
                "mail_template_id": False,
            }
        )

    @classmethod
    def tearDownClass(cls):
        teardown_test_model(
            cls.env, [OverdueReminderTester, OverdueReminderWizardTester]
        )
        super().tearDownClass()

    def test_01_overdue_reminder_letter(self):
        action = self.test_record.with_user(self.test_user_1.id).print_letter()
        self.assertEqual(action["context"].get("discard_logo_check", False), True)

    def test_02_overdue_reminder_definition(self):
        with self.assertRaises(UserError):
            self.env["reminder.definition"].create(
                {
                    "model_id": False,
                    "name": "Reminder Test 2",
                    "reminder_type": "mail",
                    "mail_template_id": False,
                }
            )

    def test_03_overdue_reminder_wizard(self):
        res = self.env["overdue.reminder.wizard.tester"].create(
            {"reminder_type": "mail", "mail_template_id": False}
        )
        # default value
        self.assertEqual(res.min_interval_days, 5)
