# Copyright 2026 CIT Services
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.exceptions import AccessError


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _is_action_report_restricted(self):
        """Returns True if the current action is restricted for the current user,
        taking group privilege inheritance into account.
        """
        self.ensure_one()
        if self.env.su:
            return False

        user_groups = self.env.user.sudo().groups_id
        return self.sudo().id in user_groups.mapped("restricted_report_action_ids").ids

    def _check_action_report_restrictions(self):
        """Raises AccessError if any action in self is restricted."""
        for action in self:
            if action._is_action_report_restricted():
                raise AccessError(
                    self.env._(
                        "You are not allowed to access this action because it "
                        "is restricted for one of your user groups."
                    )
                )

    def _get_action_dict(self):
        """Verify restrictions before loading action details for execution."""
        self._check_action_report_restrictions()
        return super()._get_action_dict()
