# Copyright 2018 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo_test_helper import FakeModelLoader

from odoo.tests import common
from odoo.tests.common import tagged

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


@tagged("post_install", "-at_install")
class TierTierValidation(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TierTierValidation, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
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
            {
                "name": "John",
                "login": "test1",
                "groups_id": [(6, 0, group_ids)],
                "email": "john@yourcompany.example.com",
            }
        )
        cls.test_user_2 = cls.env["res.users"].create(
            {"name": "Mike", "login": "test2", "email": "mike@yourcompany.example.com"}
        )
        cls.test_user_3 = cls.env["res.users"].create(
            {"name": "Mary", "login": "test3", "email": "mary@yourcompany.example.com"}
        )

        # Create tier definitions:
        cls.tier_def_obj = cls.env["tier.definition"]

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        return super(TierTierValidation, cls).tearDownClass()

    def test_definition_server_action(self):
        server_action = self.env["ir.actions.server"].create(
            {
                "name": "Check test_field value",
                "model_id": self.tester_model.id,
                "state": "code",
                "code": "action = record.test_field > 5",
            }
        )
        self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_1.id,
                "definition_type": "server_action",
                "definition_server_action_id": server_action.id,
            }
        )
        test_record = self.test_model.create({"test_field": 2.5})
        reviews = test_record.with_user(self.test_user_2).request_validation()
        self.assertFalse(reviews)
        test_record = self.test_model.create({"test_field": 6})
        reviews = test_record.with_user(self.test_user_3.id).request_validation()
        self.assertTrue(reviews)
