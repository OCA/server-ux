# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase


class TestBaseActionVisibilityRestrictionDomain(TransactionCase):
    def setUp(self):
        super(TestBaseActionVisibilityRestrictionDomain, self).setUp()
        self.model_res_users = self.env["ir.model"].search(
            [("model", "=", "res.users")]
        )
        self.model_ir_action_action = self.env["ir.actions.actions"]
        self.user_admin = self.browse_ref("base.user_admin").id
        self.group_hide_action = self.env["res.groups"].create(
            {"name": "Hide action test", "users": [(4, self.user_admin)]}
        )
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

    def test_server_actions(self):
        sa_restr = self.env["ir.actions.restriction"].create(
            {
                "server_action_id": self.server_action.id,
            }
        )
        sa_restr.read()
        actions = (
            self.model_ir_action_action.with_user(self.user_admin)
            .with_context(active_ids=[self.user_admin])
            .get_bindings("res.users")
        )
        action_ids = [a["id"] for a in actions["action"]]
        self.assertIn(self.server_action.id, action_ids)
        self.server_action.with_user(self.user_admin).with_context(
            active_ids=[self.user_admin]
        ).run()

        sa_restr.group_id = self.group_hide_action.id
        self.model_ir_action_action.clear_caches()
        actions = (
            self.model_ir_action_action.with_user(self.user_admin)
            .with_context(active_ids=[self.user_admin])
            .get_bindings("res.users")
        )
        action_ids = [a["id"] for a in actions["action"]]
        self.assertNotIn(self.server_action.id, action_ids)
        with self.assertRaises(AccessError):
            self.server_action.with_user(self.user_admin).with_context(
                active_ids=[self.user_admin]
            ).run()

        sa_restr.condition_domain = [("id", "<", 1)]
        self.model_ir_action_action.clear_caches()
        actions = (
            self.model_ir_action_action.with_user(self.user_admin)
            .with_context(active_ids=[self.user_admin])
            .get_bindings("res.users")
        )
        action_ids = [a["id"] for a in actions["action"]]
        self.assertIn(self.server_action.id, action_ids)
        with self.assertRaises(AccessError):
            self.server_action.with_user(self.user_admin).with_context(
                active_ids=[self.user_admin]
            ).run()

        sa_restr.condition_domain = [("id", ">", 1)]
        self.server_action.with_user(self.user_admin).with_context(
            active_ids=[self.user_admin]
        ).run()

    def test_window_actions(self):
        wa_restr = self.env["ir.actions.restriction"].create(
            {
                "window_action_id": self.window_action.id,
            }
        )
        wa_restr.read()
        self.window_action.with_user(self.user_admin).with_context(
            active_ids=[self.user_admin]
        ).read()

        wa_restr.group_id = self.group_hide_action.id
        with self.assertRaises(AccessError):
            self.window_action.with_user(self.user_admin).with_context(
                active_ids=[self.user_admin]
            ).read()

        wa_restr.condition_domain = [("id", "<", 1)]
        with self.assertRaises(AccessError):
            self.window_action.with_user(self.user_admin).with_context(
                active_ids=[self.user_admin]
            ).read()

        wa_restr.condition_domain = [("id", ">", 1)]
        self.window_action.with_user(self.user_admin).with_context(
            active_ids=[self.user_admin]
        ).read()
