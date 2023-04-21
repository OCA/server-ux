# Copyright 2023 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import _, models
from odoo.exceptions import UserError


class TierValidation(models.AbstractModel):
    _inherit = "tier.validation"

    def _validate_tier(self, tiers=False):
        for tier in tiers.filtered(lambda x: x.definition_id.signature):
            record = self.env[tier.model].browse(tier.res_id)
            signature_field = tier.definition_id.signature_field_id
            if not record[signature_field.name]:
                raise UserError(_("%s is required") % signature_field.field_description)
        super()._validate_tier(tiers=tiers)
