# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SignRequest(models.Model):
    _name = "sign.request"
    _inherit = ["sign.request", "tier.validation"]
    _state_from = ["in_progress"]
    _state_to = ["done"]

    def action_confirm(self):
        super().action_confirm()
        self.request_validation()

    def _notify_accepted_reviews(self):
        super()._notify_accepted_reviews()
        self._action_done()

    @api.model
    def _get_under_validation_exceptions(self):
        """Add signature field to allow write value in validation process."""
        return super()._get_under_validation_exceptions() + ["signature"]
