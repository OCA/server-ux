# Copyright 2018 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tests import Form, tagged

from odoo.addons.base_tier_validation.tests.common import CommonTierValidation


@tagged("post_install", "-at_install")
class TierTierValidation(CommonTierValidation):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_01_forward_tier(self):
        # Create new test record
        test_record = self.test_model.create({"test_field": 2.5})
        # Create tier definitions
        self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_2.id,
                "definition_domain": "[('test_field', '>', 1.0)]",
                "approve_sequence": True,
                "has_forward": True,
            }
        )
        # Request validation
        review = test_record.with_user(self.test_user_2.id).request_validation()
        self.assertTrue(review)
        record = test_record.with_user(self.test_user_1.id)
        record.invalidate_recordset()
        record.review_ids[0]._compute_can_review()
        record.validate_tier()
        self.assertFalse(record.can_forward)
        # User 2 forward to user 1
        record = test_record.with_user(self.test_user_2.id)
        record.invalidate_recordset()
        self.assertTrue(record.can_forward)
        res = record.forward_tier()
        ctx = res.get("context")
        wizard = Form(
            self.env["tier.validation.forward.wizard"]
            .with_user(self.test_user_2.id)
            .with_context(**ctx)
        )
        wizard.forward_reviewer_id = self.test_user_1
        wizard.forward_description = "Please review again"
        wiz = wizard.save()
        wiz.add_forward()
        # Newly created forwarded review will have no definition
        record = test_record.with_user(self.test_user_2.id)
        record.invalidate_recordset()
        self.assertTrue(record.review_ids.filtered(lambda r: not r.definition_id))
        # User 1 validate
        res = record.with_user(self.test_user_1.id).validate_tier()
        ctx = res.get("context")
        wizard = Form(
            self.env["comment.wizard"]
            .with_user(self.test_user_1.id)
            .with_context(**ctx)
        )
        wizard.comment = "Forward tier is reviewed"
        wiz = wizard.save()
        wiz.add_comment()
        self.assertEqual(record.validation_status, "validated")
