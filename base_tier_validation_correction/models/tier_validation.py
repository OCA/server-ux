# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools.safe_eval import safe_eval


class TierValidation(models.AbstractModel):
    _inherit = "tier.validation"

    def view_tier_correction(self):
        self.ensure_one()
        # Caller document
        active_model = self.env.context.get("active_model")
        active_id = self.env.context.get("active_id")
        res_model = self.env["ir.model"].search([("model", "=", active_model)])
        doc = self.env[active_model].browse(active_id)
        # Prepare to redirect to Tier Correction
        action = self.env.ref("base_tier_validation_correction.tier_correction_action")
        result = action.sudo().read()[0]
        # Setup default values
        ctx = result.get("context", {})
        if ctx:
            ctx = safe_eval(ctx)
        ctx.update(
            {
                "default_name": "%s ..." % doc.display_name,
                "default_model_id": res_model.id,
                "default_search_name": doc.display_name,
                "default_correction_type": "reviewer",
            }
        )
        result["context"] = ctx
        items = self.env["tier.correction.item"].search(
            [("res_model", "=", active_model), ("res_id", "=", active_id)]
        )
        if len(items) > 0:  # Already has corrections, show them.
            result["domain"] = [("id", "in", items.mapped("correction_id").ids)]
        else:  # No correction, create one
            res = self.env.ref(
                "base_tier_validation_correction.tier_correction_view_form", False
            )
            result["views"] = [(res and res.id or False, "form")]
        return result
