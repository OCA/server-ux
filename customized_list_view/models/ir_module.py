# Copyright 2024 ooops404
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class Module(models.Model):
    _inherit = "ir.module.module"

    def _button_immediate_function(self, function):
        res = super(Module, self)._button_immediate_function(function)
        views_mods = self.env["custom.list.view"].search([])
        for vm in views_mods:
            for vml in vm.line_ids:
                if not vml.field_id:
                    # field was deleted during modules operation
                    vml.unlink()
            vm.button_apply_changes()
        return res
