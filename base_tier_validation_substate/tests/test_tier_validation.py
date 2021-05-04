# Copyright 2020 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests import common

from .common import setup_test_model, teardown_test_model
from .tier_validation_tester import TierValidationTester, BaseSubstateType


@common.at_install(False)
@common.post_install(True)
class TierTierValidation(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TierTierValidation, cls).setUpClass()

        setup_test_model(cls.env, [TierValidationTester])
        setup_test_model(cls.env, [BaseSubstateType])

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

        # Create substate
        # _model = cls.env.ref("base_substate.model_base_substate_type")
        # _field = _model.field_id.filtered(lambda l: l.name == "model")
        # _field.state = "manual"
        # _field.write({
        #     "selection_ids": [(0, 0, {
        #         "value": "tier.validation.tester", "name": "Tier Tester"
        #     })]
        # })

        substate_type = cls.env["base.substate.type"].create(
            {
                "name": "Tier Tester Substate",
                "model": "tier.validation.tester",
                "target_state_field": "state",
            }
        )
        target_state = cls.env["target.state.value"].create(
            {
                "name": "Draft",
                "base_substate_type_id": substate_type.id,
                "target_state_value": "draft",
            }
        )
        cls.substate_approved = cls.env["base.substate"].create(
            {
                "name": "Approved",
                "sequence": 1,
                "target_state_value_id": target_state.id,
            },
        )
        cls.substate_rejected = cls.env["base.substate"].create(
            {
                "name": "Rejected",
                "sequence": 2,
                "target_state_value_id": target_state.id,
            },
        )

        # Create tier definitions:
        cls.tier_def_obj = cls.env["tier.definition"]
        cls.tier_def_obj.create(
            {
                "model_id": cls.tester_model.id,
                "review_type": "individual",
                "reviewer_id": cls.test_user_1.id,
                "sequence": 30,
                "approved_substate_id": cls.substate_approved.id,
                "rejected_substate_id": cls.substate_rejected.id,
            }
        )

        cls.test_record = cls.test_model.create({"test_field": 2.5})


    @classmethod
    def tearDownClass(cls):
        teardown_test_model(cls.env, [TierValidationTester])
        super(TierTierValidation, cls).tearDownClass()


    def test_1_substate_approved(self):
        tier2 = self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_1.id,  # user1
                "sequence": 20,
                "approved_substate_id": self.substate_rejected.id,
            }
        )
        reviews = self.test_record.with_user(self.test_user_1.id).request_validation()
        self.assertTrue(reviews)
        record = self.test_record.with_user(self.test_user_1.id)
        record.invalidate_cache()
        with self.assertRaises(UserError):
            record.validate_tier()
        tier2.approved_substate_id = self.substate_approved
        record.validate_tier()
        self.assertEquals(record.substate_id.name, "Approved")

    def test_2_substate_rejected(self):
        tier2 = self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_2.id,  # user2
                "sequence": 20,
                "approved_substate_id": self.substate_approved.id,
                "rejected_substate_id": self.substate_rejected.id,
            }
        )
        # Approve
        reviews = self.test_record.with_user(self.test_user_1.id).request_validation()
        self.assertTrue(reviews)
        record = self.test_record.with_user(self.test_user_1.id)
        record.invalidate_cache()
        record.validate_tier()
        self.assertEquals(record.substate_id.name, "Approved")
        # Reject
        record = self.test_record.with_user(self.test_user_2.id)
        record.invalidate_cache()
        record.reject_tier()
        self.assertEquals(record.substate_id.name, "Rejected")
