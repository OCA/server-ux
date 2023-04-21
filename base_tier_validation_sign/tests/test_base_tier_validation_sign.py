# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import users

from odoo.addons.sign_oca.tests.common import TestSignOcaBase


class TestBaseTierValidationSign(TestSignOcaBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tier_def_obj = cls.env["tier.definition"]
        cls.tier_def_obj.create(
            {
                "name": "Sign request tier definition test",
                "model_id": cls.env.ref("sign_oca.model_sign_request").id,
                "signature": True,
                "review_type": "field",
                "reviewer_field_id": cls.env.ref(
                    "sign_oca.field_sign_request__partner_user_id"
                ).id,
                "signature_field_id": cls.env.ref(
                    "sign_oca.field_sign_request__signature"
                ).id,
            }
        )
        cls.request = cls._create_request(cls, cls.user.partner_id)

    def test_tier_validation_model_name(self):
        self.assertIn(
            "sign.request", self.tier_def_obj._get_tier_validation_model_names()
        )

    @users("test-user")
    def test_validation_sign_request(self):
        self.request.action_confirm()
        self.assertEqual(self.request.state, "in_progress")
        self.assertTrue(self.request.review_ids)
        request = self.request.with_user(self.env.user)
        self._signature_request(request)
        request.validate_tier()
        self.assertEqual(request.state, "done")
        self.assertTrue(request.signed_on)
