# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class IrActionsServer(models.Model):
    _inherit = "ir.actions.server"

    mass_edit_play_onchanges = fields.Json(
        string="Play onchanges from lines",
        compute="_compute_mass_edit_play_onchanges",
    )

    @api.depends("mass_edit_line_ids.apply_onchanges")
    def _compute_mass_edit_play_onchanges(self):
        for record in self:
            record.mass_edit_play_onchanges = {
                line.field_id.name: line.apply_onchanges
                for line in record.mass_edit_line_ids
            }
