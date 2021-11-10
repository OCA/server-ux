# Copyright 2018 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo_test_helper import FakeModelLoader

from odoo.tests import Form
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
        group_ids = cls.env.ref("base.group_system").ids
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
        record.invalidate_cache()
        record.validate_tier()
        self.assertFalse(record.can_forward)
        # User 2 forward to user 1
        record = test_record.with_user(self.test_user_2.id)
        record.invalidate_cache()
        self.assertTrue(record.can_forward)
        res = record.forward_tier()
        ctx = res.get("context")
        wizard = Form(
            self.env["tier.validation.forward.wizard"]
            .with_user(self.test_user_2.id)
            .with_context(ctx)
        )
        wizard.forward_reviewer_id = self.test_user_1
        wizard.forward_description = "Please review again"
        wiz = wizard.save()
        wiz.add_forward()
        # Newly created forwarded review will have no definition
        record = test_record.with_user(self.test_user_2.id)
        record.invalidate_cache()
        self.assertTrue(record.review_ids.filtered(lambda l: not l.definition_id))
        # User 1 validate
        res = record.with_user(self.test_user_1.id).validate_tier()
        ctx = res.get("context")
        wizard = Form(
            self.env["comment.wizard"].with_user(self.test_user_1.id).with_context(ctx)
        )
        wizard.comment = "Forward tier is reviewed"
        wiz = wizard.save()
        wiz.add_comment()
        self.assertTrue(record.validated)

    def test_02_forward_tier_backward(self):
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
                "backward": True,
            }
        )
        # Request validation
        review = test_record.with_user(self.test_user_2.id).request_validation()
        self.assertTrue(review)
        record = test_record.with_user(self.test_user_1.id)
        record.invalidate_cache()
        record.validate_tier()
        self.assertFalse(record.can_forward)
        self.assertFalse(record.can_backward)
        # User 2 forward to user 1
        record = test_record.with_user(self.test_user_2.id)
        record.invalidate_cache()
        self.assertTrue(record.can_forward)
        self.assertTrue(record.can_backward)
        res = record.forward_tier()
        ctx = res.get("context")
        wizard = Form(
            self.env["tier.validation.forward.wizard"]
            .with_user(self.test_user_2.id)
            .with_context(ctx)
        )
        wizard.forward_reviewer_id = self.test_user_1
        wizard.forward_description = "Please review again"
        wizard.backward = True
        wiz = wizard.save()
        wiz.add_forward()
        # Newly created forwarded review will have no definition and will have origin
        record = test_record.with_user(self.test_user_2.id)
        record.invalidate_cache()
        self.assertTrue(record.review_ids.filtered(lambda l: not l.definition_id))
        self.assertTrue(record.review_ids.filtered(lambda l: l.origin_id))
        # User 1 validate
        res = record.with_user(self.test_user_1.id).validate_tier()
        ctx = res.get("context")
        wizard = Form(
            self.env["comment.wizard"].with_user(self.test_user_1.id).with_context(ctx)
        )
        wizard.comment = "Forward tier is reviewed"
        wiz = wizard.save()
        wiz.add_comment()
        self.assertFalse(record.validated)
        # Newly created review back to the original user
        record = test_record.with_user(self.test_user_2.id)
        record.invalidate_cache()
        # There are now two tier reviews for user 2
        self.assertEqual(
            len(
                record.review_ids.filtered(lambda l: l.reviewer_id == self.test_user_2)
            ),
            2,
        )
        # User 2 does final validation
        record.validate_tier()
        self.assertTrue(record.validated)
