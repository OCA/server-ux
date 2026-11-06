# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IrActionsServerMassEditLine(models.Model):
    _inherit = "ir.actions.server.mass.edit.line"

    apply_onchanges = fields.Boolean(help="Play field onchanges before writing value")
