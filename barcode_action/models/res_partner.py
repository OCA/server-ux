# Copyright 2018 Creu Blanca
# Copyright 2020 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import json

from odoo import _, models
from odoo.tools.safe_eval import safe_eval


class ResPartner(models.Model):
    _inherit = "res.partner"

    def find_res_partner_by_ref_using_barcode(self, barcode):
        partner = self.search([("ref", "=", barcode)], limit=1)
        if not partner:
            action = self.env.ref("barcode_action.res_partner_find")
            result = action.read()[0]
            context = safe_eval(result["context"])
            context.update(
                {
                    "default_state": "warning",
                    "default_status": _(
                        "Partner with Internal Reference " "%s cannot be found"
                    )
                    % barcode,
                }
            )
            result["context"] = json.dumps(context)
            return result
        action = self.env.ref("base.action_partner_form")
        result = action.read()[0]
        res = self.env.ref("base.view_partner_form", False)
        result["views"] = [(res and res.id or False, "form")]
        result["res_id"] = partner.id
        return result
