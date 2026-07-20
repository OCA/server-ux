# Copyright 2026 Simone Rubino - PyTech
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

from odoo.addons.base_week_day.models.mixin import WEEKDAYS


class TestDateModel(models.Model):
    _inherit = "base_week_day.mixin"
    _name = "base_week_day.test.date_model"
    _description = "Test model with date fields"

    some_date = fields.Date()
    some_date_week_day = fields.Selection(
        selection=WEEKDAYS,
        compute="_compute_some_date_week_day",
    )
    some_datetime = fields.Datetime()
    some_datetime_week_day = fields.Selection(
        selection=WEEKDAYS,
        compute="_compute_some_datetime_week_day",
    )

    def _compute_some_date_week_day(self):
        for record in self:
            record.some_date_week_day = record._get_week_day(record.some_date)

    def _compute_some_datetime_week_day(self):
        for record in self:
            record.some_datetime_week_day = record._get_week_day(record.some_datetime)
