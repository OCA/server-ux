#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json

from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, new_test_user


class TestIRRule(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.edit_own_defaults_rule = cls.env.ref("base.ir_default_user_rule")

        cls.edit_all_defaults_group = cls.env["res.groups"].create(
            {
                "name": "Edit other users' defaults",
            }
        )
        cls.edit_own_defaults_rule.excluded_group_ids = cls.edit_all_defaults_group

        cls.user = new_test_user(cls.env, login="Test user")
        cls.user_default = cls.env["ir.default"].create(
            {
                "user_id": cls.user.id,
                "field_id": cls.env["ir.model.fields"].search([], limit=1).id,
                "json_value": json.dumps(True),
            }
        )

        cls.group_user = new_test_user(cls.env, login="I can edit all users' defaults")
        cls.group_user.groups_id += cls.edit_all_defaults_group

        cls.no_group_user = new_test_user(
            cls.env, login="I can't edit other users' defaults"
        )

    def test_users_edit_defaults(self):
        """Exclude a specific group from rule `Defaults: alter personal defaults`.
        Users in that group can edit other users' defaults.
        """
        # Arrange
        edit_all_defaults_group = self.edit_all_defaults_group
        edit_own_defaults_rule = self.edit_own_defaults_rule
        user = self.user
        user_default = self.user_default
        no_group_user = self.no_group_user
        group_user = self.group_user
        # pre-condition
        self.assertIn(
            edit_all_defaults_group, edit_own_defaults_rule.excluded_group_ids
        )
        self.assertEqual(user_default.user_id, user)

        # User can edit its own defaults
        user_default.with_user(user).json_value = json.dumps(True)

        # User with group can edit other users' defaults
        user_default.with_user(group_user).json_value = json.dumps(True)

        # User without group can't edit other users' defaults
        with self.assertRaises(AccessError) as ae:
            user_default.with_user(no_group_user).json_value = json.dumps(True)
        exc_message = ae.exception.args[0]
        self.assertIn("not allowed to modify", exc_message)
        self.assertIn(user_default._name, exc_message)
