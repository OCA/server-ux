# Copyright (C) 2021 Ecosoft Co., Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form, TransactionCase


class TestHrExpenseDefault(TransactionCase):
    def setUp(self):
        super(TestHrExpenseDefault, self).setUp()
        self.Group = self.env["res.groups"]

    def test_01_new_group_line(self):
        """
        Add new model access line to a group,
        I expect that line 2 will default name as line 1 and default perm_read if shared group.
        Using following context
        {'default_src_head': {'perm_read': share},
         'default_src_line': model_access,
          'default_dest_cols': ['name', 'perm_read']}
        """
        # Test create new before save
        with Form(self.Group, view="base.view_groups_form") as f:
            f.name = "Test Group"
            f.share = True
            with f.model_access.new() as l1:
                l1.name = "Test Line 1"
                l1.model_id = self.env.ref("base.model_res_users")
                self.assertTrue(l1.perm_read)
            with f.model_access.new() as l2:
                self.assertEqual(l2.name, "Test Line 1")
                self.assertFalse(l2.model_id)
                self.assertTrue(l2.perm_read)
                l2.name = "Test Line 2"
                l2.model_id = self.env.ref("base.model_res_users")
        test_group = f.save()
        # Test create new line after save
        with Form(test_group, view="base.view_groups_form") as f:
            with f.model_access.new() as l3:
                self.assertEqual(l3.name, "Test Line 2")
                self.assertFalse(l3.model_id)
                self.assertTrue(l3.perm_read)
                l3.name = "Test Line 3"
                l3.model_id = self.env.ref("base.model_res_users")
        test_group = f.save()
