# Copyright 2024 ooops404
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    def name_get(self):
        return [(rec.id, rec.xml_id) for rec in self]
