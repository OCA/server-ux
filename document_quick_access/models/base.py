# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class Base(models.AbstractModel):
    _inherit = "base"

    def get_quick_access_code(self):
        self.ensure_one()
        rule = self.env["document.quick.access.rule"].search(
            [("model_id.model", "=", self._name)], limit=1
        )
        if not rule:
            return False
        return rule.get_code(self)
