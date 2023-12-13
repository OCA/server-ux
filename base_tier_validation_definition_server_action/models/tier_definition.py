# Copyright 2023 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class TierDefinition(models.Model):
    _inherit = "tier.definition"

    definition_type = fields.Selection(
        selection_add=[("server_action", "Server Action")]
    )
    definition_server_action_id = fields.Many2one(
        comodel_name="ir.actions.server",
        string="Server Action",
        help="Server action to add validation on object",
    )
