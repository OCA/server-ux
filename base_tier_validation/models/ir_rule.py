# Copyright (C) 2023 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class IrRule(models.Model):
    _inherit = "ir.rule"

    @api.model
    def _eval_context(self):
        ctx = super()._eval_context()
        if self._context.get("from_review_systray"):
            ctx["company_ids"] = self.env.user.company_ids.ids
        return ctx
