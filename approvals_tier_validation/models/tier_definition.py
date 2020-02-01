# Copyright 2020 Ecosoft Co., Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from ast import literal_eval

from odoo import api, fields, models


class TierDefinition(models.Model):
    _inherit = "tier.definition"

    @api.model
    def _get_tier_validation_model_names(self):
        res = super(TierDefinition, self)._get_tier_validation_model_names()
        res.append("tier.approval.request")
        return res

    approval_category_id = fields.Many2one(
        comodel_name="tier.approval.category", index=True, ondelete="cascade",
    )

    @api.constrains("approval_category_id")
    def _compute_approval_category_domain(self):
        for tier in self:
            domain = literal_eval(tier.definition_domain or "[]")
            if tier.approval_category_id:
                tier.definition_type = "domain_formula"
                d = ["category_id", "=", tier.approval_category_id.id]
                if d not in domain:
                    domain.append(d)
                    tier.definition_domain = str(domain)
