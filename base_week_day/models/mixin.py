# Copyright 2026 Simone Rubino - PyTech
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models

WEEKDAYS = [
    ("0", "Monday"),
    ("1", "Tuesday"),
    ("2", "Wednesday"),
    ("3", "Thursday"),
    ("4", "Friday"),
    ("5", "Saturday"),
    ("6", "Sunday"),
]
# Use for selection fields


class WeekDayMixin(models.AbstractModel):
    _name = "base_week_day.mixin"
    _description = "Day of Week computation"

    def _get_week_day(self, value):
        return str(value.weekday()) if value else None
