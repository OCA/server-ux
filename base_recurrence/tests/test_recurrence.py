# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from freezegun import freeze_time
from odoo_test_helper import FakeModelLoader

from odoo import fields
from odoo.tests.common import SavepointCase


class RecurrenceTestCommon(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()

        # The fake class is imported here !! After the backup_registry
        from .fake_model import FakeRecurrence

        cls.loader.update_registry((FakeRecurrence,))

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    @freeze_time("2022-07-11")
    def test_recurrence_now(self):
        """
        Check recurrence called on now()
        """
        record = self.env["fake.recurrence"].create(
            {"name": "Test", "recurrence_type": "weekly", "recurrence_interval": 1}
        )

        record._set_next_recurrency_date(from_now=True)

        self.assertEqual(
            fields.Datetime.to_datetime("2022-07-18"), record.next_recurrency_date,
        )

    @freeze_time("2022-07-11")
    def test_recurrence(self):
        """
        Check recurrence called on now()
        """
        record = self.env["fake.recurrence"].create(
            {
                "name": "Test",
                "recurrence_type": "weekly",
                "recurrence_interval": 1,
                "last_recurrency_date": "2022-07-11",
            }
        )

        record._set_next_recurrency_date()

        self.assertEqual(
            fields.Datetime.to_datetime("2022-07-18"), record.next_recurrency_date,
        )

    @freeze_time("2022-07-11")
    def test_recurrence_daily(self):
        """
        Check recurrence daily
        """
        record = self.env["fake.recurrence"].create(
            {
                "name": "Test",
                "recurrence_type": "daily",
                "recurrence_interval": 1,
                "last_recurrency_date": "2022-07-11",
            }
        )

        record._set_next_recurrency_date()

        self.assertEqual(
            fields.Datetime.to_datetime("2022-07-12"), record.next_recurrency_date,
        )

    @freeze_time("2022-07-11")
    def test_recurrence_monthly(self):
        """
        Check recurrence monthly
        """
        record = self.env["fake.recurrence"].create(
            {
                "name": "Test",
                "recurrence_type": "monthly",
                "recurrence_interval": 1,
                "last_recurrency_date": "2022-07-11",
            }
        )

        record._set_next_recurrency_date()

        self.assertEqual(
            fields.Datetime.to_datetime("2022-08-11"), record.next_recurrency_date,
        )

    @freeze_time("2022-07-11")
    def test_recurrence_monthlylastday(self):
        """
        Check recurrence monthlylastday
        """
        record = self.env["fake.recurrence"].create(
            {
                "name": "Test",
                "recurrence_type": "monthlylastday",
                "recurrence_interval": 1,
                "last_recurrency_date": "2022-07-11",
            }
        )

        record._set_next_recurrency_date()

        self.assertEqual(
            fields.Datetime.to_datetime("2022-08-31"), record.next_recurrency_date,
        )

    @freeze_time("2022-01-11")
    def test_recurrence_monthlylastday_february(self):
        """
        Check recurrence monthlylastday
        """
        record = self.env["fake.recurrence"].create(
            {
                "name": "Test",
                "recurrence_type": "monthlylastday",
                "recurrence_interval": 1,
                "last_recurrency_date": "2022-01-11",
            }
        )

        record._set_next_recurrency_date()

        self.assertEqual(
            fields.Datetime.to_datetime("2022-02-28"), record.next_recurrency_date,
        )

    @freeze_time("2022-07-11")
    def test_recurrence_quarterly(self):
        """
        Check recurrence quarterly
        """
        record = self.env["fake.recurrence"].create(
            {
                "name": "Test",
                "recurrence_type": "quarterly",
                "recurrence_interval": 1,
                "last_recurrency_date": "2022-07-11",
            }
        )

        record._set_next_recurrency_date()

        self.assertEqual(
            fields.Datetime.to_datetime("2022-10-01"), record.next_recurrency_date,
        )

    @freeze_time("2022-07-11")
    def test_recurrence_semsterly(self):
        """
        Check recurrence semesterly
        """
        record = self.env["fake.recurrence"].create(
            {
                "name": "Test",
                "recurrence_type": "semesterly",
                "recurrence_interval": 1,
                "last_recurrency_date": "2022-07-11",
            }
        )

        record._set_next_recurrency_date()

        self.assertEqual(
            fields.Datetime.to_datetime("2023-01-01"), record.next_recurrency_date,
        )

    @freeze_time("2022-07-11")
    def test_recurrence_yearly(self):
        """
        Check recurrence yearly
        """
        record = self.env["fake.recurrence"].create(
            {
                "name": "Test",
                "recurrence_type": "yearly",
                "recurrence_interval": 1,
                "last_recurrency_date": "2022-07-11",
            }
        )

        record._set_next_recurrency_date()

        self.assertEqual(
            fields.Datetime.to_datetime("2023-07-11"), record.next_recurrency_date,
        )

    @freeze_time("2022-07-11")
    def test_update_recurrence_yearly(self):
        """
        Check recurrence yearly
        """
        record = self.env["fake.recurrence"].create(
            {
                "name": "Test",
                "recurrence_type": "yearly",
                "recurrence_interval": 1,
                "last_recurrency_date": "2021-07-10",
            }
        )

        record._set_next_recurrency_date()

        self.assertEqual(
            fields.Datetime.to_datetime("2022-07-10"), record.next_recurrency_date,
        )

        record._update_recurrency_date()
        self.assertEqual(
            fields.Datetime.to_datetime("2023-07-10"), record.next_recurrency_date,
        )
        self.assertEqual(
            fields.Datetime.to_datetime("2022-07-10"), record.last_recurrency_date,
        )
