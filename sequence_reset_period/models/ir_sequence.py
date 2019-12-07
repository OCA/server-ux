# Copyright (C) 2017 Creu Blanca
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models
from datetime import timedelta, date as datetime_date
from dateutil.relativedelta import relativedelta


class IrSequence(models.Model):
    _inherit = "ir.sequence"

    range_reset = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly')
    ])

    def _compute_date_from_to(self, date):
        self.ensure_one()
        date_from = date_to = date
        if self.range_reset == 'weekly':
            date_from = date_from - timedelta(days=date_from.weekday())
            date_to = date_from + timedelta(days=6)
        elif self.range_reset == 'monthly':
            date_from = datetime_date(date_from.year, date_from.month, 1)
            date_to = date_from + relativedelta(months=1)
            date_to += relativedelta(days=-1)
        elif self.range_reset == 'yearly':
            date_from = datetime_date(date_from.year, 1, 1)
            date_to = datetime_date(date_from.year, 12, 31)
        return date_from, date_to

    def _create_date_range_seq(self, date):
        self.ensure_one()
        if not self.range_reset:
            return super()._create_date_range_seq(date)
        date_from, date_to = self._compute_date_from_to(date)
        date_range = self.env['ir.sequence.date_range'].search(
            [('sequence_id', '=', self.id), ('date_from', '>=', date),
             ('date_from', '<=', date_to)], order='date_from desc', limit=1)
        if date_range:
            date_to = date_range.date_from + timedelta(days=-1)
        date_range = self.env['ir.sequence.date_range'].search(
            [('sequence_id', '=', self.id), ('date_to', '>=', date_from),
             ('date_to', '<=', date)], order='date_to desc', limit=1)
        if date_range:
            date_from = date_range.date_to + timedelta(days=1)
        seq_date_range = self.env['ir.sequence.date_range'].sudo().create({
            'date_from': date_from,
            'date_to': date_to,
            'sequence_id': self.id,
        })
        return seq_date_range
