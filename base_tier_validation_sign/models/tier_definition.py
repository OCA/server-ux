# Copyright 2023 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class TierDefinition(models.Model):
    _inherit = "tier.definition"

    signature = fields.Boolean(string="Signature")
    signature_field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Signature field",
        domain="[('model', '=', model),('ttype', '=', 'binary')]",
    )

    @api.model
    def _get_tier_validation_model_names(self):
        res = super()._get_tier_validation_model_names()
        res.append("sign.request")
        return res
