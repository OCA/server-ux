# Copyright 2026 Simone Rubino - PyTech
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import datetime

from odoo_test_helper import FakeModelLoader

from odoo import tests


class Common(tests.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()

        from .models import TestDateModel

        cls.loader.update_registry((TestDateModel,))
        cls.addClassCleanup(cls.loader.restore_registry)

        cls.records = cls.env["base_week_day.test.date_model"].create(
            [
                {
                    "some_date": datetime.date(2020, 1, day_number),
                    "some_datetime": datetime.datetime(2020, 1, day_number),
                }
                for day_number in range(1, 10)
            ]
        )
