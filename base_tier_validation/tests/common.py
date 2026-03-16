# Copyright 2018-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import Command
from odoo.orm.model_classes import add_to_registry
from odoo.tests import new_test_user

from odoo.addons.base.tests.common import BaseCommon

from .tier_validation_tester import (
    TierDefinition,
    TierValidationTester,
    TierValidationTester2,
    TierValidationTesterComputed,
)

_test_models = [
    TierValidationTester,
    TierValidationTester2,
    TierValidationTesterComputed,
    TierDefinition,
]

_new_model_names = [
    "tier.validation.tester",
    "tier.validation.tester2",
    "tier.validation.tester.computed",
]


class CommonTierValidation(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Register test models using native Odoo 19 approach
        for model_def in _test_models:
            add_to_registry(cls.registry, model_def)
        cls.registry._setup_models__(cls.env.cr, _new_model_names)
        cls.registry.init_models(
            cls.env.cr, _new_model_names, {"models_to_check": True}
        )
        # Clean up on teardown
        for model_name in _new_model_names:
            cls.addClassCleanup(cls.registry.__delitem__, model_name)

    def setUp(self):
        super().setUp()

        self.test_model = self.env["tier.validation.tester"]
        self.test_model_2 = self.env["tier.validation.tester2"]
        self.test_model_computed = self.env["tier.validation.tester.computed"]

        self.tester_model = self.env["ir.model"].search(
            [("model", "=", "tier.validation.tester")]
        )
        self.tester_model_2 = self.env["ir.model"].search(
            [("model", "=", "tier.validation.tester2")]
        )
        self.tester_model_computed = self.env["ir.model"].search(
            [("model", "=", "tier.validation.tester.computed")]
        )
        # Create a multi-company
        self.main_company = self.env.ref("base.main_company")
        self.other_company = self.env["res.company"].create(
            {"name": "Test Company Tier"}
        )

        models = (
            self.tester_model,
            self.tester_model_2,
            self.tester_model_computed,
        )
        for model in models:
            # Access record:
            self.env["ir.model.access"].create(
                {
                    "name": f"access {model.name}",
                    "model_id": model.id,
                    "perm_read": 1,
                    "perm_write": 1,
                    "perm_create": 1,
                    "perm_unlink": 1,
                }
            )

            # Define views to avoid automatic views with all fields.
            self.env["ir.ui.view"].create(
                {
                    "model": model.model,
                    "name": f"Demo view for {model}",
                    "arch": """<form>
                    <header>
                        <button name="action_confirm" type="object" string="Confirm" />
                        <field name="state" widget="statusbar" />
                    </header>
                    <sheet>
                        <field name="test_field" />
                    </sheet>
                    </form>""",
                }
            )

        # Create users:
        self.test_user_1 = new_test_user(
            self.env, name="John", login="test1", groups="base.group_system"
        )
        self.test_user_2 = new_test_user(self.env, name="Mike", login="test2")
        self.test_user_3_multi_company = new_test_user(
            self.env,
            name="Jane",
            login="test3",
            company_ids=[Command.set([self.main_company.id, self.other_company.id])],
        )
        # Create groups
        self.test_group = self.env["res.groups"].create(
            {
                "name": "TestGroup",
                "user_ids": [(4, self.test_user_1.id), (4, self.test_user_2.id)],
            }
        )
        # Create tier definitions:
        self.tier_def_obj = self.env["tier.definition"]
        self.tier_definition = self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_1.id,
                "definition_domain": "[('test_field', '=', 1.0)]",
                "sequence": 30,
            }
        )

        self.test_record = self.test_model.create({"test_field": 1.0})
        self.test_record_2 = self.test_model_2.create({"test_field": 1.0})
        self.test_record_computed = self.test_model_computed.create({"test_field": 1.0})

        self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_1.id,
                "definition_domain": "[('test_field', '>', 3.0)]",
                "approve_sequence": True,
                "notify_on_pending": False,
                "sequence": 20,
                "name": "Definition for test 19 - sequence - user 1",
            }
        )
        self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_2.id,
                "definition_domain": "[('test_field', '>', 3.0)]",
                "approve_sequence": True,
                "notify_on_pending": True,
                "sequence": 10,
                "name": "Definition for test 19 - sequence - user 2",
            }
        )
        # Create definition for test 20
        self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_1.id,
                "definition_domain": "[('test_field', '=', 0.9)]",
                "approve_sequence": False,
                "notify_on_pending": True,
                "sequence": 10,
                "name": "Definition for test 20 - no sequence -  user 1 - no sequence",
            }
        )

        self.tier_def_obj.create(
            {
                "model_id": self.tester_model_computed.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_1.id,
                "definition_domain": "[]",
                "approve_sequence": True,
                "notify_on_pending": False,
                "sequence": 20,
                "name": "Definition for computed model",
            }
        )

        # Create definition for test 30, 31
        # Main company tier definition
        self.tier_def_obj.create(
            {
                "model_id": self.tester_model_2.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_1.id,
                "definition_domain": "[('test_field', '>=', 1.0)]",
                "approve_sequence": True,
                "notify_on_pending": False,
                "sequence": 30,
                "name": "Definition for test 30 - sequence - user 1 - main company",
                "company_id": self.main_company.id,
            }
        )
        self.tier_def_obj.create(
            {
                "model_id": self.tester_model_2.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_3_multi_company.id,
                "definition_domain": "[('test_field', '>=', 1.0)]",
                "approve_sequence": True,
                "notify_on_pending": False,
                "sequence": 20,
                "name": "Definition for test 30 - sequence - user 3 - main company",
                "company_id": self.main_company.id,
            }
        )
        # Other company tier definition
        self.tier_def_obj.create(
            {
                "model_id": self.tester_model_2.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_3_multi_company.id,
                "definition_domain": "[('test_field', '>=', 1.0)]",
                "approve_sequence": True,
                "notify_on_pending": False,
                "sequence": 30,
                "name": "Definition for test 30 - sequence - user 3 - other company",
                "company_id": self.other_company.id,
            }
        )
