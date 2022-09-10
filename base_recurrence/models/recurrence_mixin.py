# Copyright 2021 ACSONE SA/NV
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class RecurrenceMixin(models.AbstractModel):

    _name = "recurrence.mixin"
    _description = "Recurrence Mixin"
    _field_last_recurrency_date = None
    _field_next_recurrency_date = None

    # Scheduling
    recurrence_type = fields.Selection(
        [
            ("daily", "Daily"),
            ("weekly", "Weekly"),
            ("monthly", "Monthly"),
            ("monthlylastday", "Monthly Last Day"),
            ("quarterly", "Quarterly"),
            ("semesterly", "Semesterly"),
            ("yearly", "Yearly"),
        ]
    )

    @api.model
    def get_relative_delta(self, recurring_rule_type, interval=1):
        """Return a relativedelta for one period.

        When added to the first day of the period,
        it gives the first day of the next period.
        """
        recurring_func = "_recurring_rule_type_" + recurring_rule_type
        if hasattr(self, recurring_func):
            return getattr(self, recurring_func)(interval=interval)
        else:
            raise NotImplementedError()

    # HELPER FUNCTIONS #
    def _recurring_rule_type_daily(self, interval):
        return relativedelta(days=interval)

    def _recurring_rule_type_weekly(self, interval):
        return relativedelta(weeks=interval)

    def _recurring_rule_type_monthly(self, interval):
        return relativedelta(months=interval)

    def _recurring_rule_type_monthlylastday(self, interval):
        return relativedelta(months=interval, day=31)

    def _recurring_rule_type_quarterly(self, interval):
        return relativedelta(months=3 * interval, day=1)

    def _recurring_rule_type_semesterly(self, interval):
        return relativedelta(months=6 * interval, day=1)

    def _recurring_rule_type_yearly(self, interval):
        return relativedelta(years=interval)

    def _get_next_recurrency_date(self):
        self.ensure_one()
        return self[self._field_last_recurrency_date] + self.get_relative_delta(
            self.recurrence_type
        )

    def _update_recurrency_date(self):
        """
            Update the last recurrency date from the next recurrency date,
            then compute the new next recurrency date.
        """
        for record in self:
            record.update(
                {
                    record._field_last_recurrency_date: record[
                        record._field_next_recurrency_date
                    ],
                }
            )
            record.update(
                {record._field_next_recurrency_date: record._get_next_recurrency_date()}
            )

    def _set_next_recurrency_date(self, from_now=False):
        """
            Set the next recurrency date from the last recurrency field value.
            This method allows to reset that last recurrency date to now().

            Usually, this is used to initialize the record first values.

        :param from_now: [description], defaults to False
        :type from_now: bool, optional
        """
        if from_now:
            self.update({self._field_last_recurrency_date: fields.Datetime.now()})
        for record in self:
            record[
                record._field_next_recurrency_date
            ] = record._get_next_recurrency_date()
            record[
                record._field_next_recurrency_date
            ] = record._get_next_recurrency_date()
