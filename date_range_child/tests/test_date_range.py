# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests.common import TransactionCase


class DateRangeTest(TransactionCase):

    def setUp(self):
        super(DateRangeTest, self).setUp()
        self.date_range = self.env['date.range']
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

    def test_overlap_allowed(self):
        self.date_range.create({
            'name': 'FS2015',
            'date_start': '2015-01-01',
            'date_end': '2015-12-31',
            'type_id': self.type.id,
        })
        self.date_range.create({
            'name': 'FS2016',
            'date_start': '2015-01-01',
            'date_end': '2016-12-31',
            'type_id': self.type.id,
        })
