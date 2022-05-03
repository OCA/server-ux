# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class TierValidation(models.AbstractModel):
    _inherit = "tier.validation"

    def _post_tier_validation(self, reviews):
        reviews._post_process()
