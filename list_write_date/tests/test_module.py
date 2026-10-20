from odoo.tests import TransactionCase


class TestModule(TransactionCase):
    def test_write_date_in_base_list_view(self):
        view = self.env.ref("base.view_users_tree")
        arch = self.env["res.users"].get_view(view_id=view.id, view_type="list")["arch"]
        self.assertIn('name="write_date"', arch)
        self.assertIn('optional="hide"', arch)
