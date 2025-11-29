# Copyright 2025 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.base.tests.common import BaseCommon


class CommonBaseSubstate(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Import the test models that are now part of the main module
        from ..models.test_models import LineTest, SaleTest

        # Set up model references
        cls.sale_test_model = cls.env[SaleTest._name]
        cls.sale_line_test_model = cls.env[LineTest._name]

        # Create access rights for the test models if they exist
        model_names = ["base.substate.test.sale", "base.substate.test.sale.line"]
        for model_name in model_names:
            model = cls.env["ir.model"].search([("model", "=", model_name)], limit=1)
            if model:
                # Check if access already exists to avoid duplicates
                access_exists = cls.env["ir.model.access"].search(
                    [
                        ("model_id", "=", model.id),
                        ("name", "ilike", f"access {model.name}%"),
                    ],
                    limit=1,
                )
                if not access_exists:
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
        # Clean up any access rights created during tests
        model_names = ["base.substate.test.sale", "base.substate.test.sale.line"]
        for model_name in model_names:
            model = cls.env["ir.model"].search([("model", "=", model_name)], limit=1)
            if model:
                cls.env["ir.model.access"].search(
                    [
                        ("model_id", "=", model.id),
                        ("name", "ilike", f"access {model.name}%"),
                    ]
                ).unlink()
        super().tearDownClass()
