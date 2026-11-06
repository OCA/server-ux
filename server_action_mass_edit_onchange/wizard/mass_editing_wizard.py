# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MassEditingWizard(models.TransientModel):
    _inherit = "mass.editing.wizard"

    play_onchanges = fields.Json(readonly=True)

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        server_action_id = self.env.context.get("server_action_id")
        server_action = self.env["ir.actions.server"].sudo().browse(server_action_id)

        if not server_action:
            return res
        res.update(
            {
                "play_onchanges": server_action.mass_edit_play_onchanges,
            }
        )
        return res

    def _exec_write(self, server_action, vals):
        active_ids = self.env.context.get("active_ids", [])
        model = self.env[server_action.model_id.model].with_context(mass_edit=True)
        records = model.browse(active_ids)
        # Check if a field in values is set to play onchanges, in which case
        #  each record is to be updated sequentially
        onchanges_to_play = [
            fname
            for fname, val in server_action.mass_edit_play_onchanges.items()
            if val
        ]
        if onchanges_to_play:
            onchange_values = {k: v for k, v in vals.items() if k in onchanges_to_play}
            not_onchange_values = {
                k: v for k, v in vals.items() if k not in onchanges_to_play
            }
            for rec in records:
                rec_values = onchange_values.copy()
                rec_values = rec.play_onchanges(rec_values, list(rec_values.keys()))
                rec_values.update(not_onchange_values)
                rec.write(rec_values)
        else:
            # If there is not any onchange to play we can write
            #  all the records at once
            return super()._exec_write(server_action, vals)
