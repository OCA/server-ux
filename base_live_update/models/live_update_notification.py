# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import api, fields, models


class LiveUpdateNotificaiton(models.Model):
    _name = "live.update.notification"
    _description = "Model subscription for live updates"

    active = fields.Boolean(default=True)
    model_id = fields.Many2one("ir.model", required=True, ondelete="cascade")

    @api.model_create_multi
    def create(self, vals_list):
        result = super().create(vals_list)
        result._clear_notification_caches()
        return result

    def write(self, vals):
        result = super().write(vals)
        self._clear_notification_caches()
        return result

    def unlink(self):
        models = self.mapped("model_id.model")
        result = super().unlink()
        self._clear_notification_caches(models)
        return result

    def _clear_notification_caches(self, models=None):
        for model_name in models or self.mapped("model_id.model"):
            self.env[model_name]._live_update_active.clear_cache(self)
