# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tests import common
from odoo.exceptions import UserError
from .common import setup_test_model, teardown_test_model
from .tier_validation_tester import TierValidationTester


@common.at_install(False)
@common.post_install(True)
class TierTierValidation(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TierTierValidation, cls).setUpClass()

        setup_test_model(cls.env, [TierValidationTester])

        cls.test_model = cls.env[TierValidationTester._name]

        cls.tester_model = cls.env['ir.model'].search([
            ('model', '=', 'tier.validation.tester')])

        # Access record:
        cls.env["ir.model.access"].create({
            'name': "access.tester",
            'model_id': cls.tester_model.id,
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
        cls.test_user_3 = cls.env['res.users'].create({
            'name': 'Mary',
            'login': 'test3',
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

    @classmethod
    def tearDownClass(cls):
        teardown_test_model(cls.env,
                            [TierValidationTester])
        super(TierTierValidation, cls).tearDownClass()

    def test_01_reviewer_from_python_expression(self):
        tier_definition = self.tier_def_obj.create({
            'model_id': self.tester_model.id,
            'review_type': 'individual',
            'reviewer_id': self.test_user_1.id,
            'definition_type': 'formula',
            'python_code': 'rec.test_field > 1.0',
        })
        tier_definition.write({
            'model_id': self.tester_model.id,
            'review_type': 'expression',
            'python_code': 'rec.test_field > 3.0',
        })
        tier_definition.onchange_review_type()
        tier_definition.write({
            'reviewer_expression': 'rec.user_id',
        })
        self.test_record.write({
            'test_field': 3.5,
            'user_id': self.test_user_2.id,
        })
        reviews = self.test_record.sudo(
            self.test_user_3.id).request_validation()
        self.assertTrue(reviews)
        self.assertEqual(len(reviews), 2)
        record = self.test_record.sudo(self.test_user_1.id)
        self.assertIn(self.test_user_1, record.reviewer_ids)
        self.assertIn(self.test_user_2, record.reviewer_ids)
        res = self.test_model.search(
            [('reviewer_ids', 'in', self.test_user_2.id)])
        self.assertTrue(res)

    def test_02_wrong_reviewer_expression(self):
        """Error should raise with incorrect python expresions on
                tier definitions."""
        self.tier_def_obj.create({
            'model_id': self.tester_model.id,
            'review_type': 'expression',
            'reviewer_expression': 'rec.test_field',
            'python_code': 'rec.test_field > 1.0',
        })
        with self.assertRaises(UserError):
            self.test_record.sudo(self.test_user_3.id).request_validation()

    def test_03_definition_from_domain_formula(self):
        self.tier_def_obj.create({
            'model_id': self.tester_model.id,
            'review_type': 'individual',
            'reviewer_id': self.test_user_1.id,
            'definition_type': 'domain_formula',
            'definition_domain': '[("test_field", "<", 5.0)]',
            'python_code': 'rec.test_field > 1.0',
        })
        self.test_record.write({
            'test_field': 3.5,
            'user_id': self.test_user_2.id,
        })
        reviews = self.test_record.sudo(
            self.test_user_3.id).request_validation()
        self.assertTrue(reviews)
