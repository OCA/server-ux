# Copyright 2026 CIT Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IrModelAccess(models.Model):
    _inherit = "ir.model.access"

    perm_import = fields.Boolean("Import Access", default=True)
