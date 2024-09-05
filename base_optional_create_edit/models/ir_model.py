# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IrModel(models.Model):

    _inherit = "ir.model"

    avoid_create_edit = fields.Boolean()
