# Copyright (c) 2022 brain-tec AG (https://braintec.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo_test_helper import FakeModelLoader

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

        # Create tier definitions:
        cls.tier_def_obj = cls.env["tier.definition"]
        cls.tier_def_obj.create(
            {
                "model_id": cls.tester_model.id,
                "review_type": "individual",
                "reviewer_id": cls.test_user_1.id,
                "definition_domain": "[('test_field', '>', 1.0)]",
                "approve_sequence": True,
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
                "sequence": 10,
                "name": "Test definition 2 -  user 2",
            }
        )

        cls.test_record = cls.test_model.create({"test_field": 2.5})

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super(TierTierValidation, cls).tearDownClass()

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
