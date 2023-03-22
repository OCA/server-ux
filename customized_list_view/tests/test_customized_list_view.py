# Copyright 2024 ooops404
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestCustomizedListView(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestCustomizedListView, cls).setUpClass()
        cls.view_model = cls.env["ir.ui.view"].sudo()
        cls.users_model = cls.env["ir.model"]._get("res.users")
        cls.view_users_tree = cls.env.ref("base.view_users_tree")

    def test_all_customized_list_view(self):
        new_view = self.view_users_tree.copy()
        # Lets create some custom.list.view records
        login_field = self.env["ir.model.fields"].search(
            [
                ("model_id", "=", self.users_model.id),
                ("name", "=", "login"),
            ]
        )
        date_field = self.env["ir.model.fields"].search(
            [
                ("model_id", "=", self.users_model.id),
                ("name", "=", "create_date"),
            ]
        )
        write_field = self.env["ir.model.fields"].search(
            [
                ("model_id", "=", self.users_model.id),
                ("name", "=", "write_date"),
            ]
        )
        custom = self.env["custom.list.view"].create(
            {
                "name": "Test View Mod",
                "model_id": self.users_model.id,
                "list_view_id": self.view_users_tree.id,
            }
        )
        self.env["custom.list.view.line"].create(
            [
                {
                    "custom_list_view_id": custom.id,
                    "field_id": date_field.id,
                    "after": login_field.id,
                    "label": "Custom Label 1",
                },
                {
                    "custom_list_view_id": custom.id,
                    "field_id": date_field.id,
                    "before": write_field.id,
                    "label": "Custom Label 2",
                },
            ]
        )

        # New field should not be in the view before button_apply_changes is clicked
        users_form = self.view_users_tree.arch
        self.assertNotIn(
            "create_date", users_form, msg="create_date should not be in the view."
        )

        # Apply changes. Now new field should be there
        custom.button_apply_changes()
        users_form = self.view_users_tree.arch
        self.assertIn(
            "create_date", users_form, msg="create_date should be in the view."
        )

        # Try to roll back. New field should not be in the view.
        custom.button_roll_back()
        users_form = self.view_users_tree.arch
        self.assertNotIn(
            "create_date", users_form, msg="Roll back feature does not work."
        )

        # Trigger _compute_fields_domain with read(). No domain there.
        custom.list_view_id = new_view
        fields_domain = custom.line_ids[0].read(["fields_domain"])
        self.assertIsNotNone(fields_domain, msg="fields_domain should be empty.")
