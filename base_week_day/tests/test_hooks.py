# Copyright 2026 Simone Rubino - PyTech
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from ..hooks import populate_date_order_week_day
from .common import Common


class TestHooks(Common):
    def test_populate(self):
        """The Day of Week is populated correctly."""
        self.records.update(
            {
                "some_date_week_day": False,
            }
        )

        populate_date_order_week_day(
            self.env,
            "base_week_day",
            self.records._name,
            "some_date_week_day",
            "some_date",
        )

        self.records.invalidate_cache(
            fnames=["some_date_week_day"],
            ids=self.records.ids,
        )
        self.assertRecordValues(
            self.records,
            [
                {"some_date_week_day": str(record.some_date.weekday())}
                for record in self.records
            ],
        )
