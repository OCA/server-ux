# Copyright 2021 Sunanda Chhatbar <sunanda.chhatbar@initos.com>

from odoo.tests.common import TransactionCase


class TestResUsers(TransactionCase):
    def test_res_users(self):
        self.user_id = self.env["res.users"].create(
            {
                "name": "Export",
                "login": "abc@gmail.com",
                "groups_id": (4, self.env.ref("base.group_user").id),
            }
        )
        self.access = self.env["ir.model.access"].create(
            {
                "name": "res.partner",
                "perm_export": True,
                "model_id": self.env.ref("base.model_res_partner").id,
            }
        )
        results = self.user_id.fetch_export_models()
        if "res.partner" in results:
            self.assertEqual("res.partner", self.access.model_id.model)
