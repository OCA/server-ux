# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase


class TestBaseActionVisibilityRestriction(TransactionCase):
    def setUp(self):
        super(TestBaseActionVisibilityRestriction, self).setUp()
        self.user_admin = self.browse_ref("base.user_admin").id
        self.group_hide_action = self.env["res.groups"].create(
            {"name": "Hide action test", "users": [(4, self.user_admin)]}
        )
        self.model_res_users = self.env["ir.model"].search(
            [("model", "=", "res.users")]
        )
        self.model_ir_action_action = self.env["ir.actions.actions"]
        self.window_action = self.env["ir.actions.act_window"].create(
            {
                "name": "Dummy Window Action",
                "res_model": "res.users",
                "binding_model_id": self.model_res_users.id,
            }
        )
        self.server_action = self.env["ir.actions.server"].create(
            {
                "name": "Dummy Server Action",
                "model_id": self.model_res_users.id,
                "binding_model_id": self.model_res_users.id,
            }
        )

    def test_action_visibility_restriction(self):
        actions = self.model_ir_action_action.with_user(self.user_admin).get_bindings(
            "res.users"
        )
        action_ids = [a["id"] for a in actions["action"]]
        self.assertTrue(self.server_action.id in action_ids)
        self.assertTrue(self.window_action.id in action_ids)
        # Server action can be run
        self.server_action.with_user(self.user_admin).run()
        # Update actions to assign excluded_group_ids
        self.server_action.write(
            {"excluded_group_ids": [(4, self.group_hide_action.id)]}
        )
        self.window_action.write(
            {"excluded_group_ids": [(4, self.group_hide_action.id)]}
        )
        actions = self.model_ir_action_action.with_user(self.user_admin).get_bindings(
            "res.users"
        )
        action_ids = [a["id"] for a in actions["action"]]
        self.assertFalse(self.server_action.id in action_ids)
        self.assertFalse(self.window_action.id in action_ids)
        # Server action can't be run
        with self.assertRaises(AccessError):
            self.server_action.with_user(self.user_admin).run()
