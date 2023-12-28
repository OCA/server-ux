# Copyright (c) 2022 brain-tec AG (https://braintec.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo_test_helper import FakeModelLoader

from odoo.tests.common import TransactionCase, tagged

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


@tagged("post_install", "-at_install")
class TierTierValidation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TierTierValidation, cls).setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                **DISABLED_MAIL_CONTEXT,
                testing_base_tier_validation_waiting=True
            )
        )
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from odoo.addons.base_tier_validation.tests.tier_validation_tester import (
            TierValidationTester,
        )

        cls.loader.update_registry((TierValidationTester,))
        cls.test_model = cls.env[TierValidationTester._name].with_context(
            tracking_disable=True, no_reset_password=True
        )

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
                "email": "john@yourcompany.example.com",
                "groups_id": [(6, 0, group_ids)],
            }
        )
        cls.test_user_2 = cls.env["res.users"].create(
            {"name": "Mike", "login": "test2", "email": "mike@yourcompany.example.com"}
        )

        # Create tier definitions:
        cls.tier_def_obj = cls.env["tier.definition"]
        cls.tier_def_obj.create(
            {
                "model_id": cls.tester_model.id,
                "review_type": "individual",
                "reviewer_id": cls.test_user_1.id,
                "definition_domain": "[('test_field', '>', 1.0)]",
                "approve_sequence": True,
                "notify_on_pending": False,
                "sequence": 20,
                "name": "Test definition 1 - user 1",
            }
        )
        cls.tier_def_obj.create(
            {
                "model_id": cls.tester_model.id,
                "review_type": "individual",
                "reviewer_id": cls.test_user_2.id,
                "definition_domain": "[('test_field', '>', 1.0)]",
                "approve_sequence": True,
                "notify_on_pending": True,
                "sequence": 10,
                "name": "Test definition 2 -  user 2",
            }
        )
        # test 2
        cls.tier_def_obj.create(
            {
                "model_id": cls.tester_model.id,
                "review_type": "individual",
                "reviewer_id": cls.test_user_1.id,
                "definition_domain": "[('test_field', '<', 1.0)]",
                "approve_sequence": False,
                "notify_on_pending": True,
                "sequence": 10,
                "name": "Test definition 3 -  user 1 - no sequence",
            }
        )
        cls.test_record = cls.test_model.create({"test_field": 2.5})

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    def test_01_waiting_tier(self):
        # Create new test record
        tier_review_obj = self.env["tier.review"]
        test_record = self.test_model.create({"test_field": 2.5})
        # Request validation
        review = test_record.request_validation()

        self.assertTrue(review)
        # both reviews should be waiting when created
        review_1 = tier_review_obj.browse(review.ids[0])
        review_2 = tier_review_obj.browse(review.ids[1])
        self.assertTrue(review_1.status == "waiting")
        self.assertTrue(review_2.status == "waiting")
        # and then normal workflow will follow...
        review_1._compute_can_review()
        self.assertTrue(review_1.status == "pending")
        # first reviewer does not want notifications
        # chatter should be empty
        self.assertFalse(test_record.message_ids)
        self.assertTrue(review_2.status == "waiting")
        record = test_record.with_user(self.test_user_1.id)
        record.invalidate_model()
        record.validate_tier()
        self.assertTrue(review_1.status == "approved")
        self.assertTrue(review_2.status == "pending")
        # Check notify
        msg = test_record.message_ids[0].body
        request = test_record.with_user(
            self.test_user_1.id
        )._notify_requested_review_body()
        self.assertIn(request, msg)
        record.invalidate_model()
        record = test_record.with_user(self.test_user_2.id)
        record.invalidate_model()
        record.validate_tier()
        self.assertTrue(review_2.status == "approved")

    def test_02_no_sequence(self):
        # Create new test record
        tier_review_obj = self.env["tier.review"]
        test_record2 = self.test_model.create({"test_field": 0.5})
        # request validation
        review = test_record2.request_validation()
        self.assertTrue(review)
        review_1 = tier_review_obj.browse(review.ids[0])
        self.assertTrue(review_1.status == "waiting")
        review_1._compute_can_review()
        self.assertTrue(review_1.status == "pending")
        msg2 = test_record2.message_ids[0].body
        request = test_record2._notify_requested_review_body()
        self.assertIn(request, msg2)
