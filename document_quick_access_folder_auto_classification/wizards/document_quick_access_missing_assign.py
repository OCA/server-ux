# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class DocumentQuickAccessMissingAssign(models.TransientModel):
    _name = "document.quick.access.missing.assign"
    _description = "document.quick.access.missing.assign"

    @api.model
    def document_quick_access_models(self):
        models = self.env["document.quick.access.rule"].search([]).mapped("model_id")
        res = []
        for model in models:
            res.append((model.model, model.name))
        return res

    object_id = fields.Reference(
        selection=lambda r: r.document_quick_access_models(), required=True
    )
    exchange_record_id = fields.Many2one("edi.exchange.record", required=True)

    def manually_assign(self):
        self.ensure_one()
        self.exchange_record_id.backend_id.with_context(
            force_object_process=self.object_id
        ).exchange_process(self.exchange_record_id)
        return True
