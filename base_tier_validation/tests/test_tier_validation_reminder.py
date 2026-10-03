# Copyright 2018-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from freezegun import freeze_time

from odoo import fields
from odoo.tests.common import tagged

from .common import CommonTierValidation


@tagged("post_install", "-at_install")
class TierTierValidation(CommonTierValidation):
    def test_validation_reminder_skips_waiting_reviews(self):
        """Only reviews whose turn it is are reminded: a waiting review is
        not the reviewer's turn yet. Once it becomes pending, it is reminded."""
        self.tier_def_obj.search([]).notify_reminder_delay = 1
        record = self.test_model.create({"test_field": 4.0})
        record.with_user(self.test_user_2).request_validation()
        reviews = record.review_ids

        in_2_days = fields.Datetime.add(fields.Datetime.now(), days=2)
        with freeze_time(in_2_days):
            self.tier_def_obj._cron_send_review_reminder()
        reminded = reviews.filtered("last_reminder_date")
        waiting = reviews.filtered(lambda r: r.status == "waiting")
        self.assertTrue(reminded)
        self.assertEqual(set(reminded.mapped("status")), {"pending"})
        self.assertTrue(waiting)
        self.assertFalse(any(waiting.mapped("last_reminder_date")))

        # Its turn comes: the review is reminded at the next run.
        waiting[0].status = "pending"
        in_3_days = fields.Datetime.add(fields.Datetime.now(), days=3)
        with freeze_time(in_3_days):
            self.tier_def_obj._cron_send_review_reminder()
        self.assertEqual(waiting[0].last_reminder_date, in_3_days)

    def test_validation_reminder_skips_orphan_waiting_review(self):
        """A waiting review whose model is gone is left alone."""
        self.tier_definition.notify_reminder_delay = 1
        orphan = self.env["tier.review"].create(
            {
                "definition_id": self.tier_definition.id,
                "model": "tier.validation.uninstalled",
                "res_id": 1,
            }
        )
        self.assertEqual(orphan.status, "waiting")
        with freeze_time(fields.Datetime.add(fields.Datetime.now(), days=2)):
            self.tier_def_obj._cron_send_review_reminder()
        self.assertEqual(orphan.status, "waiting")
        self.assertFalse(orphan.last_reminder_date)

    def test_validation_reminder(self):
        """Check the posting of reminder to reviews."""
        tier_definition = self.tier_definition
        tier_definition.notify_reminder_delay = 3

        # Request a review today
        self.test_record.with_user(self.test_user_2.id).request_validation()
        review = self.env["tier.review"].search(
            [("definition_id", "=", tier_definition.id)]
        )
        self.assertTrue(review)
        self.assertEqual(review.last_reminder_date, False)

        # 2 days later no reminder should be posted
        in_2_days = fields.Datetime.add(fields.Datetime.now(), days=2)
        with freeze_time(in_2_days):
            tier_definition._cron_send_review_reminder()
        self.assertEqual(review.last_reminder_date, False)
        # 4 days later first reminder
        in_4_days = fields.Datetime.add(fields.Datetime.now(), days=4)
        with freeze_time(in_4_days):
            self.tier_definition._cron_send_review_reminder()
        self.assertEqual(review.last_reminder_date, in_4_days)
        # 5 days later no new reminder
        in_6_days = fields.Datetime.add(fields.Datetime.now(), days=6)
        with freeze_time(in_6_days):
            self.tier_definition._cron_send_review_reminder()
        self.assertEqual(review.last_reminder_date, in_4_days)
        # 9 days later second reminder
        in_9_days = fields.Datetime.add(fields.Datetime.now(), days=9)
        with freeze_time(in_9_days):
            self.tier_definition._cron_send_review_reminder()
        self.assertEqual(review.last_reminder_date, in_9_days)
