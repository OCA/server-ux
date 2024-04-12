# Copyright 2022 Tecnativa - David Vidal
# Copyright 2024 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class Announcement(models.Model):
    _inherit = "announcement"

    @api.model
    def announcement_full_size(self):
        return (
            self.env["ir.config_parameter"].sudo().get_param("announcement.full_size")
        )
