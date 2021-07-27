# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tests import common
from odoo.exceptions import ValidationError
from odoo.tests.common import Form
from .common import setup_test_model, teardown_test_model
from .tier_validation_tester import TierValidationTester, TierValidationTester2


@common.at_install(False)
@common.post_install(True)
class TierTierValidation(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TierTierValidation, cls).setUpClass()

        setup_test_model(cls.env,
                         [TierValidationTester, TierValidationTester2])

        cls.test_model = cls.env[TierValidationTester._name]
        cls.test_model_2 = cls.env[TierValidationTester2._name]

        cls.tester_model = cls.env['ir.model'].search([
            ('model', '=', 'tier.validation.tester')])
        cls.tester_model_2 = cls.env['ir.model'].search([
            ('model', '=', 'tier.validation.tester2')])

        # Access record:
        cls.env["ir.model.access"].create({
            'name': "access.tester",
            'model_id': cls.tester_model.id,
            'perm_read': 1,
            'perm_write': 1,
            'perm_create': 1,
            'perm_unlink': 1,
        })
        cls.env["ir.model.access"].create({
            'name': "access.tester2",
            'model_id': cls.tester_model_2.id,
            'perm_read': 1,
            'perm_write': 1,
            'perm_create': 1,
            'perm_unlink': 1,
        })

        # Create users:
        group_ids = cls.env.ref('base.group_system').ids
        cls.test_user_1 = cls.env['res.users'].create({
            'name': 'John',
            'login': 'test1',
            'groups_id': [(6, 0, group_ids)],
        })
        cls.test_user_2 = cls.env['res.users'].create({
            'name': 'Mike',
            'login': 'test2',
        })

        # Create tier definitions:
        cls.tier_def_obj = cls.env['tier.definition']
        cls.tier_def_obj.create({
            'model_id': cls.tester_model.id,
            'review_type': 'individual',
            'reviewer_id': cls.test_user_1.id,
            'definition_domain': "[('test_field', '>', 1.0)]",
        })

        cls.test_record = cls.test_model.create({
            'test_field': 2.5,
        })
        cls.test_record_2 = cls.test_model_2.create({
            'test_field': 2.5,
        })

    @classmethod
    def tearDownClass(cls):
        teardown_test_model(cls.env,
                            [TierValidationTester, TierValidationTester2])
        super(TierTierValidation, cls).tearDownClass()

    def test_01_auto_validation(self):
        """When the user can validate all future reviews, it is not needed
        to request a validation, the action can be done straight forward."""
        self.test_record.sudo(self.test_user_1.id).action_confirm()
        self.assertEqual(self.test_record.state, 'confirmed')

    def test_02_no_auto_validation(self):
        """User with no right to validate future reviews must request a
        validation."""
        with self.assertRaises(ValidationError):
            self.test_record.sudo(self.test_user_2.id).action_confirm()

    def test_03_request_validation_approved(self):
        """User 2 request a validation and user 1 approves it."""
        self.assertFalse(self.test_record.review_ids)
        reviews = self.test_record.sudo(
            self.test_user_2.id).request_validation()
        self.assertTrue(reviews)
        record = self.test_record.sudo(self.test_user_1.id)
        record.validate_tier()
        self.assertTrue(record.validated)

    def test_04_request_validation_rejected(self):
        """Request validation, rejection and reset."""
        self.assertFalse(self.test_record.review_ids)
        reviews = self.test_record.sudo(
            self.test_user_2.id).request_validation()
        self.assertTrue(reviews)
        record = self.test_record.sudo(self.test_user_1.id)
        record.reject_tier()
        self.assertTrue(record.review_ids)
        self.assertTrue(record.rejected)
        record.restart_validation()
        self.assertFalse(record.review_ids)

    def test_05_under_validation(self):
        """Write is forbidden in a record under validation."""
        self.assertFalse(self.test_record.review_ids)
        reviews = self.test_record.sudo(
            self.test_user_2.id).request_validation()
        self.assertTrue(reviews)
        record = self.test_record.sudo(self.test_user_1.id)
        with self.assertRaises(ValidationError):
            record.write({'test_field': 0.5})

    def test_06_validation_process_open(self):
        """Operation forbidden while a validation process is open."""
        self.assertFalse(self.test_record.review_ids)
        reviews = self.test_record.sudo(
            self.test_user_2.id).request_validation()
        self.assertTrue(reviews)
        record = self.test_record.sudo(self.test_user_1.id)
        with self.assertRaises(ValidationError):
            record.action_confirm()

    def test_07_search_reviewers(self):
        """Test search methods."""
        reviews = self.test_record.sudo(
            self.test_user_2.id).request_validation()
        self.assertTrue(reviews)
        record = self.test_record.sudo(self.test_user_1.id)
        self.assertIn(self.test_user_1, record.reviewer_ids)
        res = self.test_model.search(
            [('reviewer_ids', 'in', self.test_user_1.id)])
        self.assertTrue(res)

    def test_08_search_validated(self):
        """Test for the validated search method."""
        self.test_record.sudo(self.test_user_2.id).request_validation()
        res = self.test_model.sudo(self.test_user_1.id).search(
            [('validated', '=', False)])
        self.assertTrue(res)

    def test_10_systray_counter(self):
        # Create new test record
        test_record = self.test_model.create({
            'test_field': 2.5,
        })
        # Create tier definitions for both tester models
        self.tier_def_obj.create({
            'model_id': self.tester_model.id,
            'review_type': 'individual',
            'reviewer_id': self.test_user_1.id,
            'definition_domain': "[('test_field', '>', 1.0)]",
        })
        self.tier_def_obj.create({
            'model_id': self.tester_model.id,
            'review_type': 'individual',
            'reviewer_id': self.test_user_1.id,
            'definition_domain': "[('test_field', '>', 1.0)]",
        })
        self.tier_def_obj.create({
            'model_id': self.tester_model_2.id,
            'review_type': 'individual',
            'reviewer_id': self.test_user_1.id,
            'definition_domain': "[('test_field', '>', 1.0)]",
        })
        # Request validation
        self.test_record.sudo(self.test_user_2.id).request_validation()
        test_record.sudo(self.test_user_2.id).request_validation()
        self.test_record_2.sudo(self.test_user_2.id).request_validation()
        # Get review user count as systray icon would do and check count value
        docs = self.test_user_1.sudo(
            self.test_user_1).review_user_count()
        for doc in docs:
            if doc.get('name') == 'tier.validation.tester2':
                self.assertEqual(doc.get('pending_count'), 1)
            else:
                self.assertEqual(doc.get('pending_count'), 2)

    def test_11_add_comment(self):
        # Create new test record
        test_record = self.test_model.create({
            'test_field': 2.5,
        })
        # Create tier definitions
        self.tier_def_obj.create({
            'model_id': self.tester_model.id,
            'review_type': 'individual',
            'reviewer_id': self.test_user_1.id,
            'definition_domain': "[('test_field', '>', 1.0)]",
            'has_comment': True,
        })
        # Request validation
        review = test_record.sudo(self.test_user_2.id).request_validation()
        self.assertTrue(review)
        record = test_record.sudo(self.test_user_1.id)
        res = record.validate_tier()
        ctx = res.get('context')
        wizard = Form(self.env['comment.wizard'].with_context(ctx))
        wizard.comment = 'Test Comment'
        wiz = wizard.save()
        wiz.add_comment()
        self.assertTrue(test_record.review_ids.mapped('comment'))
        # Check notify
        comment = test_record.sudo(self.test_user_1.id)._notify_accepted_reviews_body()
        self.assertEqual(comment, 'A review was accepted. (Test Comment)')
        comment = test_record.sudo(self.test_user_1.id)._notify_rejected_review_body()
        self.assertEqual(comment, 'A review was rejected by John. (Test Comment)')

    def test_12_approve_sequence(self):
        # Create new test record
        test_record = self.test_model.create({
            'test_field': 2.5,
        })
        # Create tier definitions
        self.tier_def_obj.create({
            'model_id': self.tester_model.id,
            'review_type': 'individual',
            'reviewer_id': self.test_user_1.id,
            'definition_domain': "[('test_field', '>', 1.0)]",
            'approve_sequence': True,
            'sequence': 30,
        })
        self.tier_def_obj.create({
            'model_id': self.tester_model.id,
            'review_type': 'individual',
            'reviewer_id': self.test_user_2.id,
            'definition_domain': "[('test_field', '>', 1.0)]",
            'approve_sequence': True,
            'sequence': 10,
        })
        # Request validation
        self.assertFalse(self.test_record.review_ids)
        reviews = test_record.sudo(self.test_user_2.id).request_validation()
        self.assertTrue(reviews)

        docs1 = self.test_user_2.sudo(self.test_user_1).review_user_count()
        for doc in docs1:
            self.assertEqual(doc.get('pending_count'), 1)
        docs2 = self.test_user_2.sudo(self.test_user_2).review_user_count()
        for doc in docs2:
            self.assertEqual(doc.get('pending_count'), 0)

        record1 = test_record.sudo(self.test_user_1.id)
        self.assertTrue(record1.can_review)
        record2 = test_record.sudo(self.test_user_2.id)
        self.assertFalse(record2.can_review)

    def test_13_test_review_by_res_users_field(self):
        selected_field = self.env["ir.model.fields"].search(
            [("model", "=", self.test_model._name), ("name", "=", "user_id")]
        )
        test_record = self.test_model.create(
            {"test_field": 2.5, "user_id": self.test_user_2.id}
        )

        definition = self.env["tier.definition"].create(
            {
                "model_id": self.tester_model.id,
                "review_type": "field",
                "reviewer_field_id": selected_field.id,
                "definition_domain": "[('test_field', '>', 1.0)]",
                "approve_sequence": True,
            }
        )

        reviews = test_record.request_validation()
        review = reviews.filtered(lambda r: r.definition_id == definition)
        self.assertTrue(review)
        self.assertEqual(review.reviewer_ids, self.test_user_2)
