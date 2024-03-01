from odoo import fields, models


class View(models.Model):
    _inherit = "ir.ui.view"

    mass_server_action_id = fields.Many2one("ir.actions.server")
