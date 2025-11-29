# Copyright 2025 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.orm.model_classes import add_to_registry

from odoo.addons.base.tests.common import BaseCommon


class CommonBaseSubstate(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from .sale_test import (
            BaseSubstateType,
            LineTest,
            SaleTest,
        )

        add_to_registry(cls.registry, SaleTest)
        add_to_registry(cls.registry, LineTest)
        add_to_registry(cls.registry, BaseSubstateType)

        cls.registry._setup_models__(
            cls.env.cr,
            ["base.substate.test.sale", "base.substate.test.sale.line"],
        )
        cls.registry.init_models(
            cls.env.cr,
            ["base.substate.test.sale", "base.substate.test.sale.line"],
            {"models_to_check": True},
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
        cls.addClassCleanup(cls.registry.__delitem__, "base.substate.test.sale")
        cls.addClassCleanup(cls.registry.__delitem__, "base.substate.test.sale.line")
        return super().tearDownClass()
