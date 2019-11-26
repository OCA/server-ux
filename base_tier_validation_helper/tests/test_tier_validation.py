# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common
from odoo.exceptions import ValidationError
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
        cls.group_ids = cls.env.ref('base.group_system').ids
        cls.test_user_1 = cls.env['res.users'].create({
            'name': 'John',
            'login': 'test1',
            'groups_id': [(6, 0, cls.group_ids)],
        })
        cls.test_user_2 = cls.env['res.users'].create({
            'name': 'Mike',
            'login': 'test2',
        })

    @classmethod
    def tearDownClass(cls):
        teardown_test_model(cls.env,
                            [TierValidationTester])
        super(TierTierValidation, cls).tearDownClass()

    def test_01_type_individual(self):
        # No line_ids
        helper = self.env['tier.definition.helper'].create({
            'model_id': self.tester_model.id,
            'review_type': 'individual',
            'definition_type': 'domain',
        })
        self.assertEqual(helper.state, 'draft')
        self.assertEqual(len(helper.line_ids.mapped('tier_definition_id')), 0)
        with self.assertRaises(ValidationError):
            helper.button_create_tier()
        # 1 line_ids
        self.env['tier.definition.helper.line'].create({
            'helper_id': helper.id,
            'approval_level': 1,
            'name': 'Test',
            'reviewer_id': self.test_user_1.id,
        })
        # Create Tier Definition
        helper.button_create_tier()
        self.assertEqual(helper.state, 'done')
        self.assertEqual(len(helper.line_ids.mapped('tier_definition_id')), 1)

    def test_02_type_group(self):
        # No line_ids
        helper = self.env['tier.definition.helper'].create({
            'model_id': self.tester_model.id,
            'review_type': 'group',
            'definition_type': 'domain',
        })
        self.assertEqual(helper.state, 'draft')
        self.assertEqual(len(helper.line_ids.mapped('tier_definition_id')), 0)
        with self.assertRaises(ValidationError):
            helper.button_create_tier()

        # 1 line_ids
        self.env['tier.definition.helper.line'].create({
            'helper_id': helper.id,
            'approval_level': 1,
            'name': 'Test',
            'reviewer_group_id': self.env.ref('base.group_system').id,
        })
        helper.button_create_tier()
        self.assertEqual(helper.state, 'done')
        self.assertEqual(len(helper.line_ids.mapped('tier_definition_id')), 1)

    def test_03_check_button(self):
        helper = self.env['tier.definition.helper'].create({
            'model_id': self.tester_model.id,
            'review_type': 'individual',
            'definition_type': 'domain',
        })
        self.env['tier.definition.helper.line'].create({
            'helper_id': helper.id,
            'approval_level': 1,
            'name': 'Test',
            'reviewer_id': self.test_user_1.id,
        })
        # Create Tier Definition
        helper.button_create_tier()
        self.assertEqual(helper.state, 'done')
        self.assertEqual(len(helper.line_ids.mapped('tier_definition_id')), 1)
        # Delete Tier Definition
        helper.button_delete_tier()
        self.assertEqual(helper.state, 'draft')
        self.assertEqual(len(helper.line_ids.mapped('tier_definition_id')), 0)
        # Copy
        helper2 = helper.copy()
        self.assertNotEqual(helper.name, helper2.name)
