# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import AccessError, UserError
from odoo.tests import Form
from odoo.tests.common import users

from .common import TestSignOcaBase


class TestSignOca(TestSignOcaBase):
    def _create_request_custom(self, user, partner):
        self.env.user = user
        return super()._create_request(partner)

    def test_request_misc(self):
        request = self.request
        self.assertEqual(request.partner_id, self.partner)
        # error - request in draft state
        with self.assertRaises(UserError):
            request.action_done()
        request.action_confirm()
        self.assertEqual(request.state, "in_progress")
        self.assertIn(self.partner, request.message_partner_ids)
        # error -request without signature
        with self.assertRaises(UserError):
            request.action_done()
        # sign process
        self._signature_request(request)
        request.action_done()
        self.assertEqual(request.state, "done")
        self.assertTrue(request.signed_on)

    def test_request_acl(self):
        request_1 = self._create_request_custom(self.sign_user, self.partner)
        request_1.action_confirm()
        request_2 = self._create_request_custom(self.sign_manager_user, self.partner)
        request_2.action_confirm()
        all_requests = request_1 + request_2
        domain = [("id", "in", all_requests.ids)]
        # user
        requests = self.request_model.with_user(self.user).search(domain)
        self.assertNotIn(request_1, requests)
        # sign_user
        requests = self.request_model.with_user(self.sign_user).search(domain)
        self.assertIn(request_1, requests)
        self.assertNotIn(request_2, requests)
        # sign_manager_user
        requests = self.request_model.with_user(self.sign_manager_user).search(domain)
        self.assertIn(request_1, requests)
        self.assertIn(request_2, requests)

    @users("test-user")
    def test_request_basic_user(self):
        self.request.message_subscribe([self.env.user.partner_id.id])
        self.request = self.request.with_user(self.env.user)
        with self.assertRaises(AccessError):
            self.request.write({"state": "in_progress"})
        # action_confirm
        self.request.sudo().action_confirm()
        self.assertEqual(self.request.state, "in_progress")
        # sign process
        self._signature_request(self.request)
        self.request.action_done()
        self.assertEqual(self.request.state, "done")
        self.assertTrue(self.request.signed_on)

    @users("test-sign-oca-user")
    def test_request_oca_user(self):
        request = self._create_request(self.partner)
        self.assertEqual(request.state, "draft")
        self.assertEqual(request.user_id, self.sign_user)
        with self.assertRaises(AccessError):
            request.unlink()

    @users("test-sign-oca-user")
    def test_request_record_ref_onchange(self):
        request_form = Form(self.env["sign.request"])
        request_form.record_ref = "res.partner,%s" % self.partner.id
        self.assertEqual(request_form.partner_id, self.partner)

    @users("test-sign-oca-manager")
    def test_request_oca_manager(self):
        request = self._create_request(self.partner)
        self.assertEqual(request.state, "draft")
        self.assertEqual(request.user_id, self.sign_manager_user)
        request.unlink()

    def test_request_partners_wizard(self):
        wizard_form = Form(
            self.env["wizard.sign.request"].with_context(
                active_model=self.partner._name, active_ids=self.partner.ids
            )
        )
        wizard = wizard_form.save()
        self.assertIn(self.partner, wizard.line_ids.mapped("record_ref"))
        res = wizard.action_process()
        items = self.env[res["res_model"]].search(res["domain"])
        self.assertEqual(len(items), 1)
        self.assertIn(self.partner, items.mapped("partner_id"))
