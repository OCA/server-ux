# Copyright (c) 2022 brain-tec AG (https://braintec.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import tagged

from odoo.addons.base_tier_validation.tests.common import CommonTierValidation


@tagged("post_install", "-at_install")
class TierTierValidation(CommonTierValidation):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tier_def_obj.create(
            {
                "model_id": cls.tester_model.id,
                "review_type": "individual",
                "reviewer_id": cls.test_user_2.id,
                "definition_domain": "[('test_field', '>', 1.0)]",
                "approve_sequence": True,
                "sequence": 10,
                "name": "Test definition 2 -  user 2",
            }
        )

    def test_01_waiting_tier(self):
        # Create new test record
        tier_review_obj = self.env["tier.review"]
        test_record = self.test_model.create({"test_field": 2.5})
        # Request validation
        review = test_record.with_user(self.test_user_1.id).request_validation()
        self.assertTrue(review)
        # both reviews should be waiting when created
        review_1 = tier_review_obj.browse(review.ids[0])
        review_2 = tier_review_obj.browse(review.ids[1])
        self.assertTrue(review_1.status == "waiting")
        self.assertTrue(review_2.status == "waiting")
        # and then normal workflow will follow...
        review_1._compute_can_review()
        self.assertTrue(review_1.status == "pending")
        self.assertTrue(review_2.status == "waiting")
        record = test_record.with_user(self.test_user_1.id)
        record.invalidate_cache()
        record.validate_tier()
        self.assertTrue(review_1.status == "approved")
        self.assertTrue(review_2.status == "pending")
