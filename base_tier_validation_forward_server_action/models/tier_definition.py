# Copyright 2021 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class TierDefinition(models.Model):
    _inherit = "tier.definition"

    forwarded_server_action_id = fields.Many2one(
        comodel_name="ir.actions.server",
        string="Post Forward Action",
        domain=[("usage", "=", "ir_actions_server")],
        help="Server action triggered as soon as this step is forwarded",
    )
