from odoo.exceptions import UserError
from odoo.tests.common import tagged

from odoo.addons.base_tier_validation.tests.common import CommonTierValidation


@tagged("post_install", "-at_install")
class TierTierValidation(CommonTierValidation):
    def test_restart_enabled(self):
        """Test that the restart functionality works when not disabled."""

        # Create new test record
        test_record = self.test_model.create({"test_field": 2.5})

        # Request validation
        test_record.with_user(self.test_user_2.id).request_validation()

        # Check that the first tier is to validate
        self.assertEqual(test_record.review_ids[0].status, "pending")

        # Validate first tier
        test_record.with_user(self.test_user_1.id).validate_tier()

        # Check that the first tier is validated
        self.assertEqual(test_record.review_ids[0].status, "approved")

        # Restart the validation
        test_record.with_user(self.test_user_2.id).restart_validation()

        # Check that there is no more review on the record
        self.assertEqual(test_record.review_ids.ids, [])

    def test_restart_disabled(self):
        """Test that the restart functionality does not work when disabled."""

        # Create new test record
        test_record = self.test_model.create({"test_field": 2.5})

        # Create tier definition with restart disabled
        self.tier_def_obj.create(
            {
                "name": "Test Definition 2 - restart disabled",
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_2.id,
                "definition_domain": "[('test_field', '>', 1.0)]",
                "disable_validation_restart": True,
                "sequence": 20,
            }
        )

        # Request validation
        test_record.with_user(self.test_user_2.id).request_validation()

        # Check that the first tier is to validate
        self.assertEqual(test_record.review_ids[0].status, "pending")

        # Validate first tier
        test_record.with_user(self.test_user_1.id).validate_tier()

        # Check that the first tier is validated
        self.assertEqual(test_record.review_ids[0].status, "approved")

        # Attempt to restart the validation
        with self.assertRaises(UserError):
            test_record.with_user(self.test_user_2.id).restart_validation()

        # Check that the review first tier is still approved
        self.assertEqual(test_record.review_ids[0].status, "approved")
