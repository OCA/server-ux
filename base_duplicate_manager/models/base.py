# Copyright 2026 CIT Services
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class Base(models.AbstractModel):
    _inherit = "base"

    def copy(self, default=None):
        self.env["ir.model.access"]._check_duplicate_access(self._name)
        return super().copy(default=default)
