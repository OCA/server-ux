# Copyright 2022 Tecnativa - David
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class IrConfigParameter(models.Model):
    _inherit = "ir.config_parameter"

    @api.model
    def announcement_full_size(self):
        return self.sudo().get_param("announcement.full_size")
