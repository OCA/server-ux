# Copyright 2018 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import UserError
from odoo.tests import new_test_user
from odoo.tests.common import tagged

from odoo.addons.base_tier_validation.tests.common import CommonTierValidation


@tagged("post_install", "-at_install")
class TierTierValidation(CommonTierValidation):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user_3 = new_test_user(cls.env, name="Mary", login="test3")

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
        self.test_record.invalidate_cache()
        record.invalidate_cache()
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
            self.test_record.review_ids.invalidate_cache()
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
            self.test_record.review_ids.invalidate_cache()
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
        review = test_record.with_user(self.test_user_2).request_validation()
        with self.assertRaises(UserError):
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
