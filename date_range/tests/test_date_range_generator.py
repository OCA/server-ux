# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)nses/agpl).

import datetime

from dateutil.rrule import MONTHLY

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class DateRangeGeneratorTest(TransactionCase):

    def setUp(self):
        super(DateRangeGeneratorTest, self).setUp()
        self.generator = self.env['date.range.generator']
        self.type = self.env['date.range.type'].create(
            {'name': 'Fiscal year',
             'company_id': False,
             'allow_overlap': False})

        self.company = self.env['res.company'].create({
            'name': 'Test company',
        })
        self.company_2 = self.env['res.company'].create({
            'name': 'Test company 2',
            'parent_id': self.company.id,
        })
        self.typeB = self.env['date.range.type'].create(
            {'name': 'Fiscal year B',
             'company_id': self.company.id,
             'allow_overlap': False})

    def test_generate(self):
        generator = self.generator.create({
            'date_start': '1943-01-01',
            'name_prefix': '1943-',
            'type_id': self.type.id,
            'duration_count': 3,
            'unit_of_time': str(MONTHLY),
            'count': 4})
        generator.action_apply()
        ranges = self.env['date.range'].search(
            [('type_id', '=', self.type.id)])
        self.assertEqual(len(ranges), 4)
        range4 = ranges[3]
        self.assertEqual(range4.date_start, datetime.date(1943, 10, 1))
        self.assertEqual(range4.date_end, datetime.date(1943, 12, 31))
        self.assertEqual(range4.type_id, self.type)

    def test_generator_multicompany_1(self):
        with self.assertRaises(ValidationError):
            self.generator.create({
                'date_start': '1943-01-01',
                'name_prefix': '1943-',
                'type_id': self.typeB.id,
                'duration_count': 3,
                'unit_of_time': str(MONTHLY),
                'count': 4,
                'company_id': self.company_2.id,
            })
