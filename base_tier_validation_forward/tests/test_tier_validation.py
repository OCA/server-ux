# Copyright 2018 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tests import Form, new_test_user, tagged

from odoo.addons.base_tier_validation.tests.common import CommonTierValidation


@tagged("post_install", "-at_install")
class TierTierValidation(CommonTierValidation):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_test_user = new_test_user(cls.env, name="Clarissa", login="forward")

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

    def _test_forward_tier_multiple(self, has_comment=False):
        """Run forwarding flow with or without comments"""
        self.tier_def_obj.create(
            {
                "approve_sequence": True,
                "definition_domain": "[('test_field', '>', 1.0)]",
                "has_comment": has_comment,
                "has_forward": True,
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_1.id,
                "sequence": 2,
            }
        )
        self.tier_def_obj.create(
            {
                "approve_sequence": True,
                "definition_domain": "[('test_field', '>', 1.0)]",
                "has_comment": True,
                "has_forward": True,
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_2.id,
                "sequence": 1,
            }
        )
        # Create new test record
        test_record = self.test_model.create({"test_field": 2.5})
        test_record.with_user(self.test_user_2.id).request_validation()
        self.env.invalidate_all()
        self.assertRecordValues(
            test_record.review_ids,
            [
                {
                    "reviewer_id": self.test_user_1.id,
                    "status": "pending",
                },
                {
                    "reviewer_id": self.test_user_2.id,
                    "status": "waiting",
                },
            ],
        )
        # Forward the first review
        action = test_record.with_user(self.test_user_1).forward_tier()
        self.env[action["res_model"]].with_user(self.test_user_1).with_context(
            **action["context"]
        ).create(
            {
                "forward_reviewer_id": self.other_test_user.id,
                "forward_description": "Have a look",
            }
        ).add_forward()
        # The forwarded review is now in status 'forwarded',
        # The new review is in state 'pending',
        # and the remaining review is in status 'waiting'.
        self.assertRecordValues(
            test_record.review_ids,
            [
                {
                    "reviewer_id": self.test_user_1.id,
                    "status": "forwarded",
                },
                {
                    "reviewer_id": self.other_test_user.id,
                    "status": "pending",
                },
                {
                    "reviewer_id": self.test_user_2.id,
                    "status": "waiting",
                },
            ],
        )

        action = test_record.with_user(self.other_test_user).validate_tier()
        if action:
            self.env[action["res_model"]].with_user(self.other_test_user).with_context(
                **action["context"]
            ).create(
                {
                    "comment": "Reviewed",
                }
            ).add_comment()

        self.assertRecordValues(
            test_record.review_ids,
            [
                {
                    "reviewer_id": self.test_user_1.id,
                    "status": "forwarded",
                },
                {
                    "reviewer_id": self.other_test_user.id,
                    "status": "approved",
                },
                {
                    "reviewer_id": self.test_user_2.id,
                    "status": "pending",
                },
            ],
        )

        action = test_record.with_user(self.test_user_2).validate_tier()
        if action:
            self.env[action["res_model"]].with_user(self.test_user_2).with_context(
                **action["context"]
            ).create(
                {
                    "comment": "Reviewed",
                }
            ).add_comment()

        self.assertRecordValues(
            test_record.review_ids,
            [
                {
                    "reviewer_id": self.test_user_1.id,
                    "status": "forwarded",
                },
                {
                    "reviewer_id": self.other_test_user.id,
                    "status": "approved",
                },
                {
                    "reviewer_id": self.test_user_2.id,
                    "status": "approved",
                },
            ],
        )
        self.assertEqual(test_record.validation_status, "validated")

    def test_02_forward_tier_multiple_with_comment(self):
        """Expected flow with forwards and comments"""
        # Create tier definitions with a different sequence
        self._test_forward_tier_multiple(has_comment=True)

    def test_03_forward_tier_multiple_without_comment(self):
        """Expected flow with forwards, but without comments"""
        self._test_forward_tier_multiple(has_comment=False)

    def test_04_forward_notification_subtype_xmlid(self):
        """The forwarded notification subtype must reference the correct module."""
        test_record = self.test_model.create({"test_field": 2.5})
        expected = "base_tier_validation_forward.mt_tier_validation_forwarded"
        self.assertEqual(test_record._get_forwarded_notification_subtype(), expected)
        # Verify the xmlid resolves to an actual record
        subtype = self.env.ref(expected)
        self.assertEqual(subtype.name, "Tier Validation Forward Notification")

    def test_05_forward_message_uses_correct_subtype(self):
        """Forward must post a chatter message with the correct subtype."""
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
        test_record = self.test_model.create({"test_field": 2.5})
        test_record.with_user(self.test_user_2).request_validation()

        # Forward from user_2 to other_test_user
        action = test_record.with_user(self.test_user_2).forward_tier()
        self.env[action["res_model"]].with_user(self.test_user_2).with_context(
            **action["context"]
        ).create(
            {
                "forward_reviewer_id": self.other_test_user.id,
                "forward_description": "Please check",
            }
        ).add_forward()

        # The forwarded notification must use the correct subtype
        fwd_subtype = self.env.ref(
            "base_tier_validation_forward.mt_tier_validation_forwarded"
        )
        fwd_msg = self.env["mail.message"].search(
            [
                ("model", "=", "tier.validation.tester"),
                ("res_id", "=", test_record.id),
                ("subtype_id", "=", fwd_subtype.id),
            ],
            limit=1,
        )
        self.assertTrue(
            fwd_msg,
            "Forward notification must use subtype "
            "'base_tier_validation_forward.mt_tier_validation_forwarded', "
            "not fall back to 'mail.mt_note'",
        )

    def test_06_forward_target_subscribed_as_follower(self):
        """Forward target must be subscribed as follower of the record."""
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
        test_record = self.test_model.create({"test_field": 2.5})
        test_record.with_user(self.test_user_2).request_validation()

        target_partner = self.other_test_user.partner_id
        followers_before = test_record.message_follower_ids.mapped("partner_id")
        self.assertNotIn(target_partner, followers_before)

        action = test_record.with_user(self.test_user_2).forward_tier()
        self.env[action["res_model"]].with_user(self.test_user_2).with_context(
            **action["context"]
        ).create(
            {
                "forward_reviewer_id": self.other_test_user.id,
                "forward_description": "Please check",
            }
        ).add_forward()

        test_record.invalidate_recordset()
        followers_after = test_record.message_follower_ids.mapped("partner_id")
        self.assertIn(
            target_partner,
            followers_after,
            "Forward target must be subscribed as follower to receive "
            "email notifications about the forwarded review",
        )
