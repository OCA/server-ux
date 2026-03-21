# Copyright 2026 Ecosoft Co., Ltd. (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command

from odoo.addons.base_tier_validation_correction.tests.test_tier_validation import (
    TierTierValidation,
)


class TestTierCorrectionEnhance(TierTierValidation):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.correction_wizard = cls.env["tier.correction.wizard"]

    def test_01_view_tier_correction_wizard(self):
        """Test view_tier_correction opens the wizard instead of standard form."""
        # User 2 requests validation
        doc_user2 = self.test_record.with_user(self.test_user_2.id)
        doc_user2.request_validation()

        # User 1 is the reviewer as specified in the tier.definition
        doc_user1 = self.test_record.with_user(self.test_user_1.id)
        doc_user1.invalidate_recordset()
        self.assertTrue(doc_user1.can_review)

        # Call view_tier_correction should return wizard action
        action = doc_user1.view_tier_correction()

        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "tier.correction.wizard")
        self.assertEqual(action["view_mode"], "form")
        self.assertEqual(action["target"], "new")
        self.assertEqual(action["context"]["active_model"], doc_user1._name)
        self.assertEqual(action["context"]["active_id"], doc_user1.id)

        ctx = {
            "active_id": self.test_record.id,
            "active_model": self.test_record._name,
        }
        wizard = self.correction_wizard.with_context(**ctx).create({})

        # No tier.correction.rule configured, should return all users
        all_users = self.env["res.users"].search([])
        self.assertEqual(wizard.line_ids.allowed_reviewer_ids, all_users)

        # Verify wizard fields were set correctly
        self.assertEqual(wizard.res_model, self.test_record._name)
        self.assertEqual(wizard.res_id, self.test_record.id)
        # Should have lines for pending reviews
        self.assertTrue(wizard.line_ids)
        for line in wizard.line_ids:
            self.assertTrue(line.review_id)
            self.assertTrue(line.original_reviewer_id)
            # Initially new_reviewer_id should match original
            self.assertEqual(line.original_reviewer_id, line.new_reviewer_id)

    def test_02_wizard_action_confirm_no_change(self):
        """Test action_confirm when no reviewers are changed."""
        # User 2 requests validation
        doc_user2 = self.test_record.with_user(self.test_user_2.id)
        doc_user2.request_validation()

        # Create wizard with context
        ctx = {
            "active_id": self.test_record.id,
            "active_model": self.test_record._name,
        }
        wizard = self.correction_wizard.with_context(**ctx).create({})

        # Confirm without changing any reviewers
        wizard.action_confirm()

        # No tier.correction records should be created
        corrections = self.env["tier.correction"].search(
            [("name", "ilike", self.test_record.display_name)]
        )
        self.assertFalse(corrections)

    def test_03_wizard_action_confirm_with_change(self):
        """Test action_confirm when reviewers are changed."""
        tier_review_obj = self.env["tier.review"]
        # User 2 requests validation
        doc_user2 = self.test_record.with_user(self.test_user_2.id)
        review = doc_user2.request_validation()
        self.assertTrue(review)
        review_1 = tier_review_obj.browse(review.ids[0])
        review_1.invalidate_model()
        self.assertFalse(doc_user2.can_review)

        # User 1 is the reviewer as specified in tier.definition
        doc_user1 = self.test_record.with_user(self.test_user_1.id)
        doc_user1.invalidate_model()
        self.assertTrue(doc_user1.can_review)

        # Create wizard with context
        ctx = {
            "active_id": self.test_record.id,
            "active_model": self.test_record._name,
        }
        wizard = self.correction_wizard.with_context(**ctx).create({})

        # Change reviewer from user 1 to user 2
        for line in wizard.line_ids:
            line.new_reviewer_id = self.test_user_2.id
        result = wizard.action_confirm()

        # Should return close action
        self.assertEqual(result["type"], "ir.actions.act_window_close")

        # Verify reviewer was changed - now user 2 can review
        doc_user2.invalidate_model()
        self.assertTrue(doc_user2.can_review)
        doc_user1.invalidate_model()
        self.assertFalse(doc_user1.can_review)

    def test_04_allowed_reviewers_with_config(self):
        """Test allowed_reviewer_ids follows rule when configured."""
        # Create tier.correction.rule for test_record's model
        model_id = self.env["ir.model"].search(
            [("model", "=", self.test_record._name)], limit=1
        )
        # Add rule line for test_user_1 -> can only change to test_user_2
        self.env["tier.correction.rule"].create(
            {
                "model_id": model_id.id,
                "line_ids": [
                    Command.create(
                        {
                            "reviewer_from_ids": [Command.set([self.test_user_1.id])],
                            "reviewer_to_ids": [Command.set([self.test_user_2.id])],
                        }
                    )
                ],
            }
        )

        # User 2 requests validation
        doc_user2 = self.test_record.with_user(self.test_user_2.id)
        doc_user2.request_validation()

        ctx = {
            "active_id": self.test_record.id,
            "active_model": self.test_record._name,
        }
        wizard = self.correction_wizard.with_context(**ctx).create({})

        # Should only allow test_user_2 as reviewer
        self.assertEqual(len(wizard.line_ids.mapped("allowed_reviewer_ids")), 1)
        self.assertEqual(
            wizard.line_ids.mapped("allowed_reviewer_ids"), self.test_user_2
        )
