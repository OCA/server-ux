# Copyright 2018 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo_test_helper import FakeModelLoader

from odoo.exceptions import UserError
from odoo.tests import common
from odoo.tests.common import tagged

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


@tagged("post_install", "-at_install")
class TierTierValidation(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TierTierValidation, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from odoo.addons.base_tier_validation.tests.tier_validation_tester import (
            TierValidationTester,
        )

        cls.loader.update_registry((TierValidationTester,))
        cls.test_model = cls.env[TierValidationTester._name]

        cls.tester_model = cls.env["ir.model"].search(
            [("model", "=", "tier.validation.tester")]
        )

        # Access record:
        cls.env["ir.model.access"].create(
            {
                "name": "access.tester",
                "model_id": cls.tester_model.id,
                "perm_read": 1,
                "perm_write": 1,
                "perm_create": 1,
                "perm_unlink": 1,
            }
        )

        # Create users:
        group_ids = cls.env.ref("base.group_system").ids
        cls.test_user_1 = cls.env["res.users"].create(
            {
                "name": "John",
                "login": "test1",
                "groups_id": [(6, 0, group_ids)],
                "email": "john@yourcompany.example.com",
            }
        )
        cls.test_user_2 = cls.env["res.users"].create(
            {"name": "Mike", "login": "test2", "email": "mike@yourcompany.example.com"}
        )
        cls.test_user_3 = cls.env["res.users"].create(
            {"name": "Mary", "login": "test3", "email": "mary@yourcompany.example.com"}
        )

        # Create tier definitions:
        cls.tier_def_obj = cls.env["tier.definition"]
        cls.tier_def_obj.create(
            {
                "model_id": cls.tester_model.id,
                "review_type": "individual",
                "reviewer_id": cls.test_user_1.id,
                "definition_domain": "[('test_field', '>', 1.0)]",
            }
        )

        cls.test_record = cls.test_model.create({"test_field": 2.5})

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        return super(TierTierValidation, cls).tearDownClass()

    def test_01_reviewer_from_python_expression(self):
        tier_definition = self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_1.id,
                "definition_type": "formula",
                "python_code": "rec.test_field > 1.0",
            }
        )
        tier_definition.write(
            {
                "model_id": self.tester_model.id,
                "review_type": "expression",
                "python_code": "rec.test_field > 3.0",
            }
        )
        tier_definition.onchange_review_type()
        tier_definition.write({"reviewer_expression": "rec.user_id"})
        self.test_record.write({"test_field": 3.5, "user_id": self.test_user_2.id})
        reviews = self.test_record.with_user(self.test_user_3.id).request_validation()
        self.assertTrue(reviews)
        self.assertEqual(len(reviews), 2)
        record = self.test_record.with_user(self.test_user_1.id)
        self.test_record.invalidate_recordset()
        record.invalidate_recordset()
        self.assertIn(self.test_user_1, record.reviewer_ids)
        self.assertIn(self.test_user_2, record.reviewer_ids)
        res = self.test_model.search([("reviewer_ids", "in", self.test_user_2.id)])
        self.assertTrue(res)

    def test_02_wrong_reviewer_expression(self):
        """Error should raise with incorrect python expresions on
        tier definitions."""
        self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "expression",
                "reviewer_expression": "rec.test_field",
                "python_code": "rec.test_field > 1.0",
            }
        )
        with self.assertRaises(UserError):
            self.test_record.with_user(self.test_user_3).request_validation()
            self.test_record.review_ids.invalidate_recordset()
            self.test_record.review_ids._compute_python_reviewer_ids()

    def test_03_evaluate_wrong_reviewer_expression(self):
        self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "expression",
                "reviewer_expression": "raise Exception",
                "python_code": "rec.test_field > 1.0",
            }
        )
        with self.assertRaises(UserError):
            self.test_record.with_user(self.test_user_3).request_validation()
            self.test_record.review_ids.invalidate_recordset()
            self.test_record.review_ids._compute_python_reviewer_ids()

    def test_04_evaluate_wrong_python_formula_expression(self):
        test_record = self.test_model.create({"test_field": 2.5})
        # Create tier definitions
        self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "expression",
                "reviewer_expression": "raise Exception",
                "python_code": "raise Exception",
            }
        )
        # Request validation
        with self.assertRaises(UserError):
            review = test_record.with_user(self.test_user_2).request_validation()
            self.test_record.evaluate_formula_tier(review)

    def test_05_definition_from_domain_formula(self):
        self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_1.id,
                "definition_type": "domain_formula",
                "definition_domain": '[("test_field", "<", 5.0)]',
                "python_code": "rec.test_field > 1.0",
            }
        )
        self.test_record.write({"test_field": 3.5, "user_id": self.test_user_2.id})
        reviews = self.test_record.with_user(self.test_user_3.id).request_validation()
        self.assertTrue(reviews)
