# Copyright 2018 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from datetime import timedelta

from odoo_test_helper import FakeModelLoader

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase, tagged


@tagged("post_install", "-at_install")
class TierTierValidation(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TierTierValidation, cls).setUpClass()

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
        group_ids = [
            cls.env.ref("base.group_system").id,
            cls.env.ref("base_tier_validation_correction.group_tier_correction").id,
        ]
        cls.test_user_1 = cls.env["res.users"].create(
            {"name": "John", "login": "test1", "groups_id": [(6, 0, group_ids)]}
        )
        cls.test_user_2 = cls.env["res.users"].create(
            {"name": "Mike", "login": "test2"}
        )
        cls.test_user_3 = cls.env["res.users"].create(
            {"name": "Mary", "login": "test3"}
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
        super(TierTierValidation, cls).tearDownClass()

    def test_01_tier_correction(self):
        """With the document in validation,
        - User click on Change Reivewer to creat new correction
        - Change the reviewer to user 2, test that user 2 need_validation
        - Revert to user 1, test that now user 1 need validation
        - Click on Change Review link from the document again, then view the corrections
        """
        # User 2, request validation
        doc_user2 = self.test_record.with_user(self.test_user_2.id)
        doc_user2.request_validation()
        self.assertFalse(doc_user2.can_review)
        # User 1, is the reviewer as specified in the tier.definition
        doc_user1 = self.test_record.with_user(self.test_user_1.id)
        doc_user1.invalidate_cache()
        self.assertTrue(doc_user1.can_review)
        # Change Reviewer from user 1 -> user 2
        ctx = {"active_id": doc_user1.id, "active_model": doc_user1._name}
        res = doc_user1.with_context(ctx).view_tier_correction()
        self.assertFalse(res["domain"])  # No existing correction, create new
        correction = self.env["tier.correction"].create(
            {
                "name": res["context"].get("default_name"),
                "name_search": res["context"].get("default_name_search"),
                "model_id": res["context"].get("default_model_id"),
                "correction_type": res["context"].get("default_correction_type"),
                "new_reviewer_ids": [self.test_user_2.id],
                "old_reviewer_ids": [self.test_user_1.id],
            }
        )
        # Only on state = 'prepare', to allow correction
        with self.assertRaises(ValidationError):
            correction.do_correct()
        # Test cancel -> draft
        correction.action_cancel()
        self.assertEqual(correction.state, "cancel")
        correction.action_draft()
        self.assertEqual(correction.state, "draft")
        # Test view scheduled action
        action = correction.view_scheduled_action()
        self.assertEqual(action["name"], "Scheduled Actions")
        #  Continue
        correction.action_prepare()
        self.assertEqual(correction.state, "prepare")
        self.assertTrue(correction.reference)
        with self.assertRaises(ValidationError):
            correction.do_revert()
        item = correction.item_ids[0]
        self.assertEqual(item.resource_ref, self.test_record)
        self.assertEqual(item.new_reviewer_ids, correction.new_reviewer_ids)
        # View affected tier.reviews
        AffectedReview = self.env["affected.tier.reviews"]
        reviews = AffectedReview.with_context(active_id=item.id)._default_review_ids()
        self.assertTrue(reviews)
        # Make correction, now user 2 can review
        correction.action_done()
        doc_user2.invalidate_cache()
        self.assertTrue(doc_user2.can_review)
        doc_user1.invalidate_cache()
        self.assertFalse(doc_user1.can_review)
        # Make reversion, now user 1 can reivew
        correction.action_revert()
        doc_user1.invalidate_cache()
        self.assertTrue(doc_user1.can_review)
        doc_user2.invalidate_cache()
        self.assertFalse(doc_user2.can_review)
        # From the document, view tier correction once again
        res = doc_user1.with_context(ctx).view_tier_correction()
        self.assertEqual(res["domain"][0][2], [correction.id])

    def test_01_tier_correction_by_scheduler(self):
        """With the document in validation,
        - User click on Change Reivewer to creat new correction
        - Setup Scheduled Correction Date and Scheduled Revert, test date constraints
        - Run scheduler which change reviewer to user 2, test user 2 need_validation
        - Run scheduler which revert to user 1, test user 1 need validation
        """
        # User 2, request validation
        doc_user2 = self.test_record.with_user(self.test_user_2.id)
        doc_user2.request_validation()
        self.assertFalse(doc_user2.can_review)
        # User 1, is the reviewer as specified in the tier.definition
        doc_user1 = self.test_record.with_user(self.test_user_1.id)
        doc_user1.invalidate_cache()
        self.assertTrue(doc_user1.can_review)
        # Change Reviewer from user 1 -> user 2
        ctx = {"active_id": doc_user1.id, "active_model": doc_user1._name}
        res = doc_user1.with_context(ctx).view_tier_correction()
        self.assertFalse(res["domain"])  # No existing correction, create new
        correction = self.env["tier.correction"].create(
            {
                "name": res["context"].get("default_name"),
                "name_search": res["context"].get("default_name_search"),
                "model_id": res["context"].get("default_model_id"),
                "correction_type": res["context"].get("default_correction_type"),
                "new_reviewer_ids": [self.test_user_2.id],
            }
        )
        # Run Schedulder, to correct
        correction.date_schedule_correct = fields.Datetime.now()
        scheduler = self.env.ref(
            "base_tier_validation_correction.tier_correction_sechduler"
        )
        correction.action_prepare()
        self.assertEqual(correction.state, "prepare")
        scheduler.method_direct_trigger()
        doc_user2.invalidate_cache()
        self.assertTrue(doc_user2.can_review)
        doc_user1.invalidate_cache()
        self.assertFalse(doc_user1.can_review)
        # Run Schedulder, to revert
        with self.assertRaises(ValidationError):
            correction.date_schedule_revert = fields.Datetime.now() - timedelta(days=1)
        correction.date_schedule_revert = fields.Datetime.now()
        scheduler = self.env.ref(
            "base_tier_validation_correction.tier_correction_sechduler"
        )
        self.assertEqual(correction.state, "done")
        scheduler.method_direct_trigger()
        doc_user2.invalidate_cache()
        self.assertTrue(doc_user1.can_review)
        doc_user1.invalidate_cache()
        self.assertFalse(doc_user2.can_review)
