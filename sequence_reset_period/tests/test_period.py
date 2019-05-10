# Copyright 2017 Creu Blanca <https://creublanca.es/>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from odoo.tests import common
from datetime import date
from dateutil.relativedelta import relativedelta


class TestSequence(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.date = date(2018, 3, 14)

    def get_sequence(self, method):
        return self.env['ir.sequence'].create({
            'name': 'Test sequence',
            'implementation': 'standard',
            'use_date_range': True,
            'range_reset': method,
            'padding': '5'
        })

    def test_none(self):
        sequence = self.get_sequence(False)
        self.assertFalse(sequence.date_range_ids)
        self.assertEqual('00001', sequence.with_context(
            ir_sequence_date=self.date).next_by_id())
        range = sequence.date_range_ids
        self.assertTrue(range)
        self.assertEqual(date(2018, 1, 1), range.date_from)
        self.assertEqual(date(2018, 12, 31), range.date_to)

    def test_daily(self):
        sequence = self.get_sequence('daily')
        self.assertFalse(sequence.date_range_ids)
        self.assertEqual('00001', sequence.with_context(
            ir_sequence_date=self.date).next_by_id())
        range = sequence.date_range_ids
        self.assertTrue(range)
        self.assertEqual(self.date, range.date_from)
        self.assertEqual(self.date, range.date_to)

    def test_weekly(self):
        sequence = self.get_sequence('weekly')
        self.assertFalse(sequence.date_range_ids)
        self.assertEqual('00001', sequence.with_context(
            ir_sequence_date=self.date).next_by_id())
        range = sequence.date_range_ids
        self.assertTrue(range)
        self.assertEqual(date(2018, 3, 12), range.date_from)
        self.assertEqual(date(2018, 3, 18), range.date_to)

    def test_monthly(self):
        sequence = self.get_sequence('monthly')
        self.assertFalse(sequence.date_range_ids)
        self.assertEqual('00001', sequence.with_context(
            ir_sequence_date=self.date).next_by_id())
        range = sequence.date_range_ids
        self.assertTrue(range)
        self.assertEqual(date(2018, 3, 1), range.date_from)
        self.assertEqual(date(2018, 3, 31), range.date_to)

    def test_yearly(self):
        sequence = self.get_sequence('yearly')
        self.assertFalse(sequence.date_range_ids)
        self.assertEqual('00001', sequence.with_context(
            ir_sequence_date=self.date).next_by_id())
        range = sequence.date_range_ids
        self.assertTrue(range)
        self.assertEqual(date(2018, 1, 1), range.date_from)
        self.assertEqual(date(2018, 12, 31), range.date_to)

    def test_monthly_existing(self):
        sequence = self.get_sequence('monthly')
        self.env['ir.sequence.date_range'].create({
            'date_from': date(2018, 3, 1),
            'date_to': date(2018, 3, 10),
            'sequence_id': sequence.id,
        })
        self.env['ir.sequence.date_range'].create({
            'date_from': date(2018, 3, 20),
            'date_to': date(2018, 3, 25),
            'sequence_id': sequence.id,
        })
        self.assertEqual('00001', sequence.with_context(
            ir_sequence_date=self.date).next_by_id())
