# Copyright 2024 ooops404
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class Module(models.Model):
    _inherit = "ir.module.module"

    def _button_immediate_function(self, function):
        res = super(Module, self)._button_immediate_function(function)
        clv_model = self.env["ir.model"]._get("custom.list.view")
        if not clv_model:
            # case when customized_list_view was uninstalled
            # views will be restored in the uninstall_hook
            return res
        line_mods = self.env["custom.list.view.line"].search([("field_id", "=", False)])
        if line_mods:
            # fields was deleted during modules operation
            custom_views = line_mods.mapped("custom_list_view_id")
            line_mods.unlink()
            custom_views.button_apply_changes()
        return res
