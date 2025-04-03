# Copyright 2018 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import tagged

from odoo.addons.base_tier_validation.tests.common import CommonTierValidation


@tagged("post_install", "-at_install")
class TierTierValidation(CommonTierValidation):
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
        reviews = test_record.with_user(
            self.test_user_3_multi_company.id
        ).request_validation()
        self.assertTrue(reviews)
