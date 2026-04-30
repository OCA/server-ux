# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestBaseAutomationSalesTeamSubscribe(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_partner = cls.env["res.partner"].create({"name": "Target Record"})

        cls.user_1 = cls.env["res.users"].create(
            {
                "name": "Team Member 1",
                "login": "member1",
                "email": "m1@test.com",
            }
        )
        cls.user_2 = cls.env["res.users"].create(
            {
                "name": "Team Member 2",
                "login": "member2",
                "email": "m2@test.com",
            }
        )

        cls.sales_team = cls.env["crm.team"].create(
            {
                "name": "Test Sales Team",
                "member_ids": [
                    Command.link(cls.user_1.id),
                    Command.link(cls.user_2.id),
                ],
            }
        )

        cls.automation = cls.env["base.automation"].create(
            {
                "name": "Test Team Subscription",
                "model_id": cls.env.ref("base.model_res_partner").id,
                "trigger": "on_create_or_write",
                "state": "followers",
                "subscribe_team_ids": [Command.link(cls.sales_team.id)],
            }
        )

    def test_team_subscription_on_write(self):
        existing_followers = self.test_partner.message_follower_ids.mapped("partner_id")
        self.assertNotIn(self.user_1.partner_id, existing_followers)
        self.assertNotIn(self.user_2.partner_id, existing_followers)

        self.test_partner.write({"comment": "Triggering automation"})

        followers = self.test_partner.message_follower_ids.partner_id
        self.assertIn(self.user_1.partner_id, followers)
        self.assertIn(self.user_2.partner_id, followers)

    def test_mixed_subscription(self):
        extra_partner = self.env["res.partner"].create({"name": "Manual Follower"})
        self.automation.write({"partner_ids": [Command.link(extra_partner.id)]})

        new_record = self.env["res.partner"].create({"name": "Brand New Record"})

        followers = new_record.message_follower_ids.partner_id
        self.assertIn(extra_partner, followers)
        self.assertIn(self.user_1.partner_id, followers)
        self.assertIn(self.user_2.partner_id, followers)
