# Copyright 2026 CIT Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import Command
from odoo.tests.common import TransactionCase


class TestBaseImportManager(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        polluted_columns = [
            ("res_partner", "autopost_bills"),
            ("res_users", "notification_type"),
        ]
        for table, column in polluted_columns:
            cls.env.cr.execute(f"""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name='{table}' AND column_name='{column}'
            """)
            if cls.env.cr.fetchone():
                cls.env.cr.execute(
                    f"ALTER TABLE {table} ALTER COLUMN {column} DROP NOT NULL"
                )

        cls.test_group_1 = cls.env["res.groups"].create({"name": "Test Group 1"})
        cls.test_group_2 = cls.env["res.groups"].create({"name": "Test Group 2"})

        user_vals = {
            "name": "Test User",
            "login": "test_user_import_1",
            "groups_id": [
                Command.set([cls.test_group_1.id, cls.env.ref("base.group_user").id])
            ],
        }
        cls.test_user = cls.env["res.users"].create(user_vals)

        cls.model_res_partner = cls.env["ir.model"]._get_id("res.partner")

        cls.env["ir.model.access"].search(
            [("model_id", "=", cls.model_res_partner)]
        ).write({"perm_import": False})

        cls.access_group_1 = cls.env["ir.model.access"].create(
            {
                "name": "Access Group 1",
                "model_id": cls.model_res_partner,
                "group_id": cls.test_group_1.id,
                "perm_read": True,
                "perm_import": False,
            }
        )

        cls.access_group_2 = cls.env["ir.model.access"].create(
            {
                "name": "Access Group 2",
                "model_id": cls.model_res_partner,
                "group_id": cls.test_group_2.id,
                "perm_read": True,
                "perm_import": True,
            }
        )

    def _get_tree(self, tag="list", target_model="res.partner"):
        tree = etree.Element(tag)
        if target_model:
            tree.set("model_access_rights", target_model)
        return tree

    def test_ir_model_access_default(self):
        access = self.env["ir.model.access"].create(
            {
                "name": "Test Access Default",
                "model_id": self.model_res_partner,
            }
        )
        self.assertTrue(access.perm_import)

    def test_ir_ui_view_no_target_model(self):
        tree = self._get_tree(target_model=False)
        processed_tree = (
            self.env["ir.ui.view"]
            .with_user(self.test_user)
            ._postprocess_access_rights(tree)
        )
        self.assertNotIn("import", processed_tree.attrib)

    def test_ir_ui_view_wrong_tag(self):
        tree = self._get_tree(tag="form")
        processed_tree = (
            self.env["ir.ui.view"]
            .with_user(self.test_user)
            ._postprocess_access_rights(tree)
        )
        self.assertNotIn("import", processed_tree.attrib)

    def test_ir_ui_view_no_import_rights_groups(self):
        tree = self._get_tree()
        processed_tree = (
            self.env["ir.ui.view"]
            .with_user(self.test_user)
            ._postprocess_access_rights(tree)
        )
        self.assertEqual(processed_tree.get("import"), "0")

    def test_ir_ui_view_with_import_rights_groups(self):
        self.test_user.write({"groups_id": [Command.link(self.test_group_2.id)]})
        tree = self._get_tree()
        processed_tree = (
            self.env["ir.ui.view"]
            .with_user(self.test_user)
            ._postprocess_access_rights(tree)
        )
        self.assertNotIn("import", processed_tree.attrib)
