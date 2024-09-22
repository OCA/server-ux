# Copyright 2024 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

UNSUPPORTED_FIELD_TYPES = ["binary", "serialized"]


class TierDefinition(models.Model):
    _inherit = "tier.definition"

    review_on_update = fields.Boolean()

    on_update_type = fields.Selection(
        selection=[
            ("all", "All Records, All Modifications"),
            ("records", "Selected Records, Selected Modifications"),
            ("fields", "All Records, Selected Modifications"),
        ],
        default=None,
    )

    on_update_record_ids = fields.Many2many(
        comodel_name="ir.model.data",
        string="On Update Records",
        domain="[('model', '=', model)]",
    )

    on_update_field_ids = fields.Many2many(
        comodel_name="ir.model.fields",
        string="On Update Fields",
        relation="tier_definition_on_update_fields_rel",
        column1="tier_definition_id",
        column2="field_id",
        domain="[('model_id', '=', model_id)]",
    )
