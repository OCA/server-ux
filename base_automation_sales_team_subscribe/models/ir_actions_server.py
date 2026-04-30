# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class IrActionsServer(models.Model):
    _inherit = "ir.actions.server"

    def _run_action_followers_multi(self, eval_context=None):
        res = super()._run_action_followers_multi(eval_context=eval_context)

        if self.usage == "base_automation":
            automation = (
                self.env["base.automation"]
                .sudo()
                .search([("action_server_id", "=", self.id)], limit=1)
            )

            if automation and automation.subscribe_team_ids:
                Model = self.env[self.model_name]
                if hasattr(Model, "message_subscribe"):
                    team_partners = automation.subscribe_team_ids.mapped(
                        "member_ids.partner_id"
                    )
                    partners_to_add = team_partners - self.partner_ids

                    if partners_to_add:
                        records = Model.browse(
                            self._context.get("active_ids")
                            or self._context.get("active_id")
                        )
                        records.message_subscribe(partner_ids=partners_to_add.ids)
        return res
