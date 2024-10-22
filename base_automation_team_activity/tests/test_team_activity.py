# Copyright 2024 Binhex - Adasat Torres
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("-at_install", "post_install")
class TestTeamActivity(TransactionCase):
    def setUp(self):
        super().setUp()

        self.admin_user = self.env.ref("base.user_root")
        self.team_id = self.env["mail.activity.team"].create(
            {
                "name": "Test Team",
                "user_id": self.admin_user.id,
            }
        )
        self.contact_id = self.env["res.partner"].create(
            {"name": "Test Contact", "email": "test@test.com"}
        )

        self.test_automation_id = self.env["base.automation"].create(
            {
                "name": "Test",
                "active": True,
                "model_id": self.env.ref("base.model_res_partner").id,
                "trigger": "on_write",
                "trigger_field_ids": [
                    (
                        4,
                        self.env.ref("base.field_res_partner__email").id,
                    )
                ],
                "state": "next_activity",
                "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
                "activity_summary": "Test Summary",
                "activity_note": "Test Note",
                "activity_date_deadline_range": 1,
                "activity_date_deadline_range_type": "days",
                "activity_user_type": "team",
                "team_id": self.team_id.id,
            }
        )
        self.test2_automation_id = self.env["base.automation"].create(
            {
                "name": "Test2",
                "active": True,
                "model_id": self.env.ref("base.model_res_partner").id,
                "trigger": "on_write",
                "trigger_field_ids": [
                    (
                        4,
                        self.env.ref("base.field_res_partner__name").id,
                    )
                ],
                "state": "next_activity",
                "activity_type_id": False,
                "activity_summary": "Test Summary",
                "activity_note": "Test Note",
                "activity_date_deadline_range": 1,
                "activity_date_deadline_range_type": "days",
                "activity_user_type": "team",
                "team_id": self.team_id.id,
            }
        )
        self.test3_automation_id = self.env["base.automation"].create(
            {
                "name": "Test3",
                "active": True,
                "model_id": self.env.ref("base.model_res_partner").id,
                "trigger": "on_write",
                "trigger_field_ids": [
                    (
                        4,
                        self.env.ref("base.field_res_partner__name").id,
                    )
                ],
                "state": "next_activity",
                "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
                "activity_summary": "Test Summary",
                "activity_note": "Test Note",
                "activity_date_deadline_range": 1,
                "activity_date_deadline_range_type": "days",
                "activity_user_type": "specific",
                "activity_user_id": self.admin_user.id,
            }
        )

    def test_change_partner_email(self):
        self.assertEqual(len(self.contact_id.activity_ids), 0)
        self.contact_id.email = "test@test2.com"
        self.assertEqual(len(self.contact_id.activity_ids), 1)

    def test_fail_change_partner_name(self):
        self.test3_automation_id.active = False
        self.assertEqual(len(self.contact_id.activity_ids), 0)
        self.contact_id.name = "Test Contact 2"
        self.assertEqual(len(self.contact_id.activity_ids), 0)

    def test_normal_activity(self):
        self.test2_automation_id.active = False
        self.assertEqual(len(self.contact_id.activity_ids), 0)
        self.contact_id.name = "Test Contact 3"
        self.assertFalse(self.env.context.get("mail_activity_team_id"))
