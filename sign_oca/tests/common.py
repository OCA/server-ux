# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, common, new_test_user


class TestSignOcaBase(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")
        cls.company.country_id = cls.env.ref("base.es")
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.user = new_test_user(cls.env, login="test-user", context=ctx)
        cls.sign_user = new_test_user(
            cls.env,
            login="test-sign-oca-user",
            groups="sign_oca.sign_oca_group_user",
            context=ctx,
        )
        cls.sign_manager_user = new_test_user(
            cls.env,
            login="test-sign-oca-manager",
            groups="sign_oca.sign_oca_group_manager",
            context=ctx,
        )
        cls.request_model = cls.env["sign.request"]
        cls.request = cls._create_request(cls, cls.partner)

    def _create_request(self, partner):
        request_form = Form(self.env["sign.request"])
        request_form.partner_id = partner
        return request_form.save()

    def _signature_request(self, request):
        # sign process with custom image
        signature_demo = self.env.ref("sign_oca.attachment_sign_oca_signature_demo")
        request.write({"signature": signature_demo.sudo().datas})
