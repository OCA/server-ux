# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSequenceRangeEnd(TransactionCase):
    def setUp(self):
        super(TestSequenceRangeEnd, self).setUp()
        self.sequence_obj = self.env["ir.sequence"]
        self.sequence_code = "test.sequence"
        vals = {
            "name": "Test Sequence",
            "implementation": "standard",
            "code": self.sequence_code,
            "use_date_range": True,
            "padding": 3,
            "date_range_ids": [
                (
                    0,
                    0,
                    {
                        "date_from": "2020-10-01",
                        "date_to": "2021-09-30",
                        "number_next_actual": 1,
                    },
                )
            ],
        }
        self.test_sequence = self.sequence_obj.create(vals)

    def test_range_year(self):
        """range_year: use year of date_from
        range_end_year: use year of date_to"""
        test_date = "2021-03-10"
        # range_year
        self.test_sequence.prefix = "TEST/%(range_year)s/"
        number = self.sequence_obj.next_by_code(
            "test.sequence", sequence_date=test_date
        )
        self.assertEqual(number, "TEST/2020/001")
        # range_end_year
        self.test_sequence.prefix = "TEST/%(range_end_year)s/"
        number = self.sequence_obj.next_by_code(
            "test.sequence", sequence_date=test_date
        )
        self.assertEqual(number, "TEST/2021/002")
