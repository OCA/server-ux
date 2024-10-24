# Copyright 2024 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo_test_helper import FakeModelLoader

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestBaseTierValidationOnUpdate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Same config as in base_tier_validation but with different
        # fake models loaded
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .tier_validation_tester import (
            TierDefinition,
            TierValidationTester2Update,
            TierValidationTesterUpdate,
        )

        cls.loader.update_registry(
            (TierValidationTesterUpdate, TierValidationTester2Update, TierDefinition)
        )

        cls.test_model = cls.env[TierValidationTesterUpdate._name]
        cls.test_model_2 = cls.env[TierValidationTester2Update._name]

        cls.tester_model = cls.env["ir.model"].search(
            [("model", "=", "tier.validation.tester.update")]
        )
        cls.tester_model_2 = cls.env["ir.model"].search(
            [("model", "=", "tier.validation.tester2.update")]
        )

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
        cls.env["ir.model.access"].create(
            {
                "name": "access.tester2",
                "model_id": cls.tester_model_2.id,
                "perm_read": 1,
                "perm_write": 1,
                "perm_create": 1,
                "perm_unlink": 1,
            }
        )

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

        cls.tier_def = cls.env["tier.definition"]

        cls.tier_def.search([]).active = False
        cls.test_user_3 = cls.test_user_1.copy()

        cls.record_1 = cls.test_model.create(
            {
                "user_id": cls.test_user_1.id,
                "test_field": 10.1,
                "state": "progress",
            }
        )
        cls.record_2 = cls.test_model.create(
            {
                "user_id": cls.test_user_2.id,
                "test_field": 20.2,
                "state": "progress",
            }
        )

        user_id = cls.env["ir.model.fields"].search(
            [("model_id", "=", cls.tester_model.id), ("name", "=", "user_id")]
        )
        field_test_field = cls.env["ir.model.fields"].search(
            [("model_id", "=", cls.tester_model.id), ("name", "=", "test_field")]
        )

        cls.tv_records = cls.tier_def.create(
            {
                "name": "Tier for records",
                "model_id": cls.tester_model.id,
                "review_type": "individual",
                "reviewer_id": cls.test_user_3.id,
                "sequence": 30,
                "review_on_update": True,
                "on_update_type": "records",
                "on_update_record_ids": [(6, 0, cls.record_1.ids)],
                "on_update_field_ids": [(6, 0, [user_id.id, field_test_field.id])],
            }
        )
        cls.tv_fields = cls.tier_def.create(
            {
                "name": "Tier for fields",
                "model_id": cls.tester_model.id,
                "review_type": "individual",
                "reviewer_id": cls.test_user_1.id,
                "sequence": 30,
                "review_on_update": True,
                "on_update_type": "fields",
                "on_update_field_ids": [
                    (
                        6,
                        0,
                        [
                            user_id.id,
                            field_test_field.id,
                        ],
                    )
                ],
            }
        )

    def test_update_one_field_both_definitions(self):
        self.assertFalse(self.record_1.review_ids)
        self.record_1.write({"test_field": 101, "state": "confirmed"})
        self.record_1.invalidate_model()
        reviews = self.record_1.review_ids
        self.assertEqual(self.record_1.state, "confirmed")
        self.assertEqual(self.record_1.test_field, 10.1)
        self.assertEqual(len(reviews), 2)
        self.assertEqual(reviews.mapped("status"), ["pending", "pending"])
        # First validation, update is not applied
        self.record_1.with_user(self.test_user_1.id).validate_tier()
        self.assertEqual(self.record_1.test_field, 10.1)
        self.assertIn("approved", reviews.mapped("status"))
        self.assertIn("pending", reviews.mapped("status"))
        # Second validation, update is applied
        self.record_1.with_user(self.test_user_3.id).validate_tier()
        self.assertEqual(self.record_1.test_field, 101)
        self.assertEqual(reviews.mapped("status"), ["approved", "approved"])

    def test_update_one_field_one_definition(self):
        self.assertFalse(self.record_2.review_ids)
        self.record_2.write({"test_field": 202, "state": "confirmed"})
        self.record_2.invalidate_model()
        review = self.record_2.review_ids
        self.assertEqual(self.record_2.state, "confirmed")
        self.assertEqual(self.record_2.test_field, 20.2)
        self.assertEqual(len(review), 1)
        self.assertEqual(review.status, "pending")
        self.record_2.with_user(self.test_user_1.id).validate_tier()
        self.assertEqual(self.record_2.test_field, 202)
        self.assertEqual(self.record_2.state, "confirmed")
        self.assertEqual(review.status, "approved")

    def test_update_one_field_no_definition(self):
        self.record_2.write({"state": "confirmed"})
        self.record_2.invalidate_model()
        reviews = self.record_2.review_ids
        self.assertFalse(reviews)
        self.assertEqual(self.record_2.state, "confirmed")

    def test_update_two_fields(self):
        self.record_2.write(
            {"test_field": 500, "user_id": self.test_user_1.id, "state": "confirmed"}
        )
        self.record_2.invalidate_model()
        reviews = self.record_2.review_ids
        self.assertEqual(self.record_2.state, "confirmed")
        self.assertNotEqual(self.record_2.test_field, 500)
        self.assertNotEqual(self.record_2.user_id, self.test_user_1)
        self.assertEqual(len(reviews), 1)
        self.assertEqual(reviews.status, "pending")
        self.record_2.with_user(self.test_user_1.id).validate_tier()
        self.assertEqual(self.record_2.test_field, 500)
        self.assertEqual(self.record_2.user_id, self.test_user_1)

    def test_only_one_review_by_definition_error(self):
        self.record_2.write({"user_id": self.test_user_2.id, "state": "confirmed"})
        self.record_2.invalidate_model()
        reviews = self.record_2.review_ids
        self.assertEqual(len(reviews), 1)
        with self.assertRaises(ValidationError) as m:
            self.record_2.write(
                {
                    "user_id": self.test_user_3.id,
                }
            )
        self.assertIn(
            "have pending reviews on the following fields", m.exception.args[0]
        )
        self.record_2.with_user(self.test_user_1.id).validate_tier()
        self.record_2.write(
            {
                "user_id": self.test_user_2.id,
            }
        )

    def test_reject_one_review_no_update(self):
        self.record_2.write(
            {
                "test_field": 606,
                "user_id": self.test_user_2.id,
            }
        )
        self.record_2.invalidate_model()
        self.record_2.with_user(self.test_user_1.id).reject_tier()
        self.assertEqual(self.record_2.test_field, 20.2)

    def test_review_user_count(self):
        self.record_1.test_field = 707
        self.record_1.invalidate_model()
        self.record_1.with_user(self.test_user_1.id).validate_tier()
        count = self.test_user_3.with_user(self.test_user_3).review_user_count()
        self.assertEqual(len(count), 1)

    def test_update_regular_field_message(self):
        self.record_1.write({"test_field": 808, "state": "confirmed"})
        self.record_1.invalidate_model()
        self.record_1.with_user(self.test_user_1.id).validate_tier()
        message = self.record_1.on_update_message
        self.assertIn(self.env.user.display_name, message)
        self.assertIn("Test Field", message)
        self.assertIn("808", message)
        self.assertNotIn("confirmed", message)

    def test_update_m2o_field_message(self):
        self.record_1.write({"user_id": self.test_user_2.id, "state": "confirmed"})
        self.record_1.invalidate_model()
        self.record_1.with_user(self.test_user_1.id).validate_tier()
        message = self.record_1.on_update_message
        self.assertIn(self.env.user.display_name, message)
        self.assertIn("Requested by", message)
        self.assertIn(self.test_user_2.display_name, message)
        self.assertNotIn("confirmed", message)

    def test_update_o2m_field_message(self):
        field_tester2_ids = self.env["ir.model.fields"].search(
            [("model_id", "=", self.tester_model.id), ("name", "=", "tester2_ids")]
        )
        self.tier_def.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_1.id,
                "review_on_update": True,
                "on_update_type": "fields",
                "on_update_field_ids": [(6, 0, [field_tester2_ids.id])],
            }
        )
        record_2_1 = self.test_model_2.create({"test_field": 1, "name": "test 2.1"})
        record_2_2 = record_2_1.copy({"test_field": 2, "name": "test 2.2"})

        self.record_1.write(
            {
                "tester2_ids": [(6, 0, [record_2_1.id, record_2_2.id])],
            }
        )
        self.record_1.invalidate_model()
        message = self.record_1.on_update_message
        self.assertIn(self.env.user.display_name, message)
        self.assertIn("Tester2", message)
        self.assertIn("[ADD] test 2.1", message)
        self.assertIn("[ADD] test 2.2", message)

        self.record_1.with_user(self.test_user_1.id).validate_tier()
        self.record_1.write(
            {
                "tester2_ids": [(6, 0, [record_2_1.id])],
            }
        )
        self.record_1.invalidate_model()
        message = self.record_1.on_update_message
        self.assertIn(self.env.user.display_name, message)
        self.assertIn("Tester2", message)
        self.assertIn("[Delete] test 2.2", message)
        self.assertNotIn("[ADD] test 2.1", message)

    def test_tier_definition_on_update_all_fields_and_records(self):
        self.tier_def.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_1.id,
                "review_on_update": True,
                "on_update_type": "all",
            }
        )
        self.record_1.write({"state": "confirmed"})
        self.record_1.invalidate_model()
        self.assertEqual(len(self.record_1.review_ids), 1)
        self.assertEqual(self.record_1.review_ids.status, "pending")

    def test_multi_tier_definition_on_update(self):
        self.tv_fields.write(
            {
                "sequence": 9,
                "approve_sequence": True,
            }
        )
        self.tier_def.create(
            {
                "name": "Tier 3",
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_1.id,
                "review_on_update": True,
                "on_update_type": "all",
                "sequence": 10,
                "approve_sequence": True,
            }
        )

        self.record_2.test_field = 111
        self.record_2 = self.record_2.with_user(self.test_user_1.id)
        self.record_2.invalidate_model()
        self.assertEqual(self.record_2.test_field, 20.2)
        self.assertTrue(self.record_2.can_review)
        self.assertEqual(
            2, len(self.record_2.review_ids.filtered(lambda l: l.status == "pending"))
        )
        self.record_2.validate_tier()
        self.assertEqual(self.record_2.test_field, 20.2)
        self.assertEqual(
            1, len(self.record_2.review_ids.filtered(lambda l: l.status == "pending"))
        )
        self.record_2.validate_tier()
        self.assertEqual(
            0, len(self.record_2.review_ids.filtered(lambda l: l.status == "pending"))
        )
        self.assertEqual(self.record_2.test_field, 111)
