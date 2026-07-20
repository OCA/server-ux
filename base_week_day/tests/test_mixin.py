# Copyright 2026 Simone Rubino - PyTech
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import Common


class TestMixin(Common):
    def test_week_day(self):
        """The Day of Week is computed correctly."""
        self.assertRecordValues(
            self.records,
            [
                {
                    "some_date_week_day": str(record.some_date.weekday()),
                    "some_datetime_week_day": str(record.some_datetime.weekday()),
                }
                for record in self.records
            ],
        )
