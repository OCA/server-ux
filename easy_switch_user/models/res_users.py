from odoo import models


class ResUsers(models.Model):
    _inherit = "res.users"

    def action_switch_user(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": "/web/become/%s" % self.id,
            "target": "self",
        }
