# Copyright 2018-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo.tests import common

from .tier_validation_tester import TierValidationTester, TierValidationTester2


def setup_test_model(env, model_clses):
    for model_cls in model_clses:
        model_cls._build_model(env.registry, env.cr)

    env.registry.setup_models(env.cr)
    env.registry.init_models(
        env.cr,
        [model_cls._name for model_cls in model_clses],
        dict(env.context, update_custom_fields=True),
    )


def teardown_test_model(env, model_clses):
    for model_cls in model_clses:
        del env.registry.models[model_cls._name]
    env.registry.setup_models(env.cr)


class CommonTierValidation(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
            )
        )
        setup_test_model(cls.env, [TierValidationTester, TierValidationTester2])
        cls.test_model = cls.env[TierValidationTester._name]
        cls.test_model_2 = cls.env[TierValidationTester2._name]

        cls.tester_model = cls.env["ir.model"].search(
            [("model", "=", "tier.validation.tester")]
        )
        cls.tester_model_2 = cls.env["ir.model"].search(
            [("model", "=", "tier.validation.tester2")]
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
                "sequence": 30,
            }
        )

        cls.test_record = cls.test_model.create({"test_field": 2.5})
        cls.test_record_2 = cls.test_model_2.create({"test_field": 2.5})

    @classmethod
    def tearDownClass(cls):
        teardown_test_model(cls.env, [TierValidationTester, TierValidationTester2])
        return super().tearDownClass()
