# Copyright 2026 CIT Services
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.exceptions import AccessError


class IrActionsActions(models.Model):
    _inherit = "ir.actions.actions"

    def _is_action_action_restricted(self):
        """Returns True if the current action is restricted for the current user,
        taking group privilege inheritance into account.
        """
        self.ensure_one()
        if self.env.su:
            return False

        action_sudo = self.sudo()
        action_type = action_sudo.type
        user_groups = self.env.user.sudo().groups_id
        if action_type == "ir.actions.act_window":
            return (
                action_sudo.id in user_groups.mapped("restricted_window_action_ids").ids
            )
        if action_type == "ir.actions.server":
            return (
                action_sudo.id in user_groups.mapped("restricted_server_action_ids").ids
            )

        return (
            action_sudo.id in user_groups.mapped("restricted_window_action_ids").ids
            or action_sudo.id in user_groups.mapped("restricted_server_action_ids").ids
        )

    def _check_action_action_restrictions(self):
        """Raises AccessError if any action in self is restricted."""
        for action in self:
            if action._is_action_action_restricted():
                raise AccessError(
                    self.env._(
                        "You are not allowed to access this action because it "
                        "is restricted for one of your user groups."
                    )
                )

    def _get_action_dict(self):
        """Verify restrictions before loading action details for execution."""
        self._check_action_action_restrictions()
        return super()._get_action_dict()

    @api.model
    def get_bindings(self, model_name):
        """Filter out restricted actions from sidebars and bindings."""
        result = super().get_bindings(model_name)
        if self.env.su:
            return result
        if "action" in result:
            action_ids = list(map(lambda rep: rep.get("id"), result["action"]))
            if actions := self.browse(action_ids):
                restricted_ids = {
                    action.id
                    for action in actions
                    if action._is_action_action_restricted()
                }
                if restricted_ids:
                    result["action"] = list(
                        filter(
                            lambda rep: rep
                            if rep.get("id") not in restricted_ids
                            else {},
                            result["action"],
                        )
                    )
                if not result.get("action", False):
                    result.pop("action")
        return result
