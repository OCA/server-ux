# Copyright 2018 Creu Blanca
# Copyright 2020 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import json

from odoo import models
from odoo.fields import Domain


class ResPartner(models.Model):
    _inherit = "res.partner"

    def find_res_partner_by_ref_using_barcode(self, barcode):
        partner = self.search(Domain("ref", "=", barcode), limit=1)
        if partner:
            action = self.env["ir.actions.act_window"]._for_xml_id(
                "base.action_partner_form"
            )
            view = self.env.ref("base.view_partner_form", False)
            action["views"] = [(view.id if view else False, "form")]
            action["res_id"] = partner.id
            return action
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Find Partner"),
            "res_model": "barcode.action",
            "view_mode": "form",
            "views": [[False, "form"]],
            "target": "new",
            "context": json.dumps(
                {
                    "default_model": "res.partner",
                    "default_method": "find_res_partner_by_ref_using_barcode",
                    "default_state": "warning",
                    "default_status": self.env._(
                        "Partner with Internal Reference %s cannot be found",
                        barcode,
                    ),
                }
            ),
        }
