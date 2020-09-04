# Copyright 2020 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class TierDefinition(models.Model):
    _inherit = "tier.definition"

    approved_substate_id = fields.Many2one(
        comodel_name="base.substate",
        string="Approved Substate",
        ondelete="restrict",
        domain="[('model', '=', model)]",
        help="Set document substate when approved",
    )
    rejected_substate_id = fields.Many2one(
        comodel_name="base.substate",
        string="Rejected Substate",
        ondelete="restrict",
        domain="[('model', '=', model)]",
        help="Set document substate when rejected",
    )
