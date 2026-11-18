# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestIrModelAccess(TransactionCase):
    def test_export_denied_by_default(self):
        access_vals = {
            "name": "test access",
            "model_id": self.env["ir.model"]._get_id("res.partner"),
            "group_id": self.env.ref("base.group_user").id,
        }
        config_parameter = self.env["ir.config_parameter"].sudo()

        config_parameter.set_param(
            "base_export_manager.export_denied_by_default", "True"
        )
        access = self.env["ir.model.access"].create(access_vals)
        self.assertFalse(access.perm_export)

        config_parameter.set_param(
            "base_export_manager.export_denied_by_default", "False"
        )
        access = self.env["ir.model.access"].create(access_vals)
        self.assertTrue(access.perm_export)
