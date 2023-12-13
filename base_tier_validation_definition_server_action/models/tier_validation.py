# Copyright 2023 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, models
from odoo.exceptions import UserError


class TierValidation(models.AbstractModel):
    _inherit = "tier.validation"

    def evaluate_server_action_tier(self, tier):
        try:
            res = tier.definition_server_action_id.with_context(
                **{
                    "active_id": self.id,
                    "active_ids": [self.id],
                    "active_model": self._name,
                }
            ).run()
        except Exception as error:
            raise UserError(
                _("Error evaluating tier validation conditions.\n %s") % error
            ) from error
        return res

    def evaluate_tier(self, tier):
        res = super().evaluate_tier(tier)
        if tier.definition_type == "server_action":
            return self.evaluate_server_action_tier(tier)
        return res
