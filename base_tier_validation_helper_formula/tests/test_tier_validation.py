# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common
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

    @classmethod
    def tearDownClass(cls):
        teardown_test_model(cls.env,
                            [TierValidationTester])
        super(TierTierValidation, cls).tearDownClass()

    def test_01(self):
        reviewer_expression = 'rec.env["res.users"].search([("id", "!=", 1)])'
        python_code = 'rec.test_field > 0'
        helper = self.env['tier.definition.helper'].create({
            'model_id': self.tester_model.id,
            'review_type': 'expression',
            'definition_type': 'formula',
        })
        self.env['tier.definition.helper.line'].create({
            'helper_id': helper.id,
            'approval_level': 1,
            'name': 'Test',
            'reviewer_expression': reviewer_expression,
            'python_code': python_code,
        })
        self.assertEqual(helper.state, 'draft')
        self.assertEqual(len(helper.line_ids.mapped('tier_definition_id')), 0)
        # Create Tier Definition
        helper.button_create_tier()
        self.assertEqual(helper.state, 'done')
        self.assertEqual(len(helper.line_ids.mapped('tier_definition_id')), 1)

    def test_02(self):
        test_field = self.env['ir.model.fields'].search(
            [('model', '=', 'tier.validation.tester'), ('name', '=', 'test_field')])
        helper = self.env['tier.definition.helper'].create({
            'model_id': self.tester_model.id,
            'review_type': 'expression',
            'is_reviewers': True,
            'definition_type': 'formula',
            'is_amount_domain': True,
            'amount_ref_id': test_field.id,
            'condition_type': 'range',
        })
        self.env['tier.definition.helper.line'].create({
            'helper_id': helper.id,
            'approval_level': 1,
            'name': 'Test',
            'min_amount': 0.0,
            'max_amount': 1000.0,
        })
        self.assertEqual(helper.state, 'draft')
        self.assertEqual(len(helper.line_ids.mapped('tier_definition_id')), 0)
        # Create Tier Definition
        helper.button_create_tier()
        self.assertEqual(helper.state, 'done')
        self.assertEqual(len(helper.line_ids.mapped('tier_definition_id')), 1)
