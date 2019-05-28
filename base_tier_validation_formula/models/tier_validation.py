# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError


class TierValidation(models.AbstractModel):
    _inherit = 'tier.validation'

    @api.multi
    def evaluate_formula_tier(self, tier):
        try:
            res = safe_eval(tier.python_code, globals_dict={'rec': self})
        except Exception as error:
            raise UserError(_(
                "Error evaluating tier validation conditions.\n %s") % error)
        return res

    @api.multi
    def evaluate_tier(self, tier):
        if tier.definition_type == 'formula':
            return self.evaluate_formula_tier(tier)
        return super().evaluate_tier(tier)
