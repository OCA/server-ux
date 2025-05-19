# Copyright 2025 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo_test_helper import FakeModelLoader

from odoo.addons.base.tests.common import BaseCommon


class CommonBaseSubstate(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .sale_test import (
            BaseSubstateType,
            LineTest,
            SaleTest,
        )

        cls.loader.update_registry(
            (
                SaleTest,
                LineTest,
                BaseSubstateType,
            )
        )

        cls.sale_test_model = cls.env[SaleTest._name]
        cls.sale_line_test_model = cls.env[LineTest._name]

        models = cls.env["ir.model"].search(
            [
                (
                    "model",
                    "in",
                    ["base.substate.test.sale", "base.substate.test.sale.line"],
                )
            ]
        )
        for model in models:
            # Access record:
            cls.env["ir.model.access"].create(
                {
                    "name": f"access {model.name}",
                    "model_id": model.id,
                    "perm_read": 1,
                    "perm_write": 1,
                    "perm_create": 1,
                    "perm_unlink": 1,
                }
            )

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()
