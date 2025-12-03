# Copyright 2025 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# Copyright 2025 OERP Canada <https://www.oerp.ca>

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

        for model_class in [
            SaleTest,
            LineTest,
            BaseSubstateType,
        ]:
            add_to_registry(cls.registry, model_class)

        test_models = [
            "base.substate.test.sale",
            "base.substate.test.sale.line",
        ]
        cls.registry._setup_models__(cls.env.cr, test_models)
        cls.registry.init_models(cls.env.cr, test_models, {"models_to_check": True})
        for model_name in test_models:
            cls.addClassCleanup(cls.registry.__delitem__, model_name)

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
