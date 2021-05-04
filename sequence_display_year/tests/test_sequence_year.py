# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from datetime import date

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestSequenceDisplayYear(TransactionCase):
    def setUp(self):
        super().setUp()
        self.date = date(2020, 1, 14)

    def get_sequence(self, prefix, number=None, use_date_range=False):
        return self.env["ir.sequence"].create(
            {
                "name": "Test sequence",
                "implementation": "standard",
                "prefix": prefix,
                "number_of_year": number,
                "use_date_range": use_date_range,
                "padding": "5",
            }
        )

    def test_01_default_sequence(self):
        """ Test default sequence """
        prefix = "%(y)s-"
        sequence_default = self.get_sequence(prefix)
        sequence = sequence_default.with_context(
            ir_sequence_date=self.date
        ).next_by_id()
        self.assertEqual("20-00001", sequence)

        prefix = "%(year)s-"
        sequence_default = self.get_sequence(prefix)
        sequence = sequence_default.with_context(
            ir_sequence_date=self.date
        ).next_by_id()
        self.assertEqual("2020-00001", sequence)

    def test_02_year_be_sequence(self):
        """ Test sequence year with Buddhist Calendar """
        prefix = "%(y)s-"
        # Buddhist Calendar (B.E.)
        number_of_year = 543
        sequence_with_year = self.get_sequence(prefix, number=number_of_year)
        sequence_year = sequence_with_year.with_context(
            ir_sequence_date=self.date
        ).next_by_id()
        self.assertEqual("63-00001", sequence_year)

        # Buddhist Calendar with date range
        prefix = "%(range_y)s-"
        sequence_date_range = self.get_sequence(
            "%(range_y)-", number=number_of_year, use_date_range=True
        )
        # invalid prefix
        with self.assertRaises(UserError):
            sequence_date_range.with_context(ir_sequence_date=self.date).next_by_id()
        sequence_date_range.prefix = prefix
        sequence = sequence_date_range.with_context(
            ir_sequence_date=self.date
        ).next_by_id()
        self.assertEqual("63-00002", sequence)

        prefix = "%(year)s-"
        sequence_with_year = self.get_sequence(prefix, number=number_of_year)
        sequence_year = sequence_with_year.with_context(
            ir_sequence_date=self.date
        ).next_by_id()
        self.assertEqual("2563-00001", sequence_year)

    def test_03_year_ah_sequence(self):
        """ Test sequence year with Islamic Calendar """
        prefix = "%(y)s-"
        # Islamic Calendar (A.H.)
        number_of_year = -579
        sequence_with_year = self.get_sequence(prefix, number=number_of_year)
        sequence_year = sequence_with_year.with_context(
            ir_sequence_date=self.date
        ).next_by_id()
        self.assertEqual("41-00001", sequence_year)

        prefix = "%(year)s-"
        sequence_with_year = self.get_sequence(prefix, number=number_of_year)
        sequence_year = sequence_with_year.with_context(
            ir_sequence_date=self.date
        ).next_by_id()
        self.assertEqual("1441-00001", sequence_year)
