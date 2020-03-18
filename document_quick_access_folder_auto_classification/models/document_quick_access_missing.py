# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class DocumentQuickAccessMissing(models.Model):
    _name = "document.quick.access.missing"
    _description = "Missing Document"

    name = fields.Char(required=True, readonly=True)
    data = fields.Binary(related="attachment_id.datas", readonly=True)
    state = fields.Selection(
        [("pending", "Pending"), ("processed", "Processed"), ("deleted", "Rejected")],
        default="pending",
    )
    model = fields.Char(readonly=True)
    res_id = fields.Integer(readonly=True)
    attachment_id = fields.Many2one("ir.attachment", readonly=True)

    def assign_model(self, model, res_id):
        records = self.filtered(lambda r: r.state == "pending")
        res = self.env[model].browse(res_id)
        res.ensure_one()
        for record in records:
            record.attachment_id.write({"res_model": model, "res_id": res_id})
        records.write(self._processed_values(model, res_id))

    def _processed_values(self, model, res_id):
        return {"state": "processed", "model": model, "res_id": res_id}

    def _deleted_values(self):
        return {"state": "deleted"}

    def access_resource(self):
        self.ensure_one()
        if not self.model:
            return {}
        record = self.env[self.model].browse(self.res_id).exists()
        if not record:
            return {}
        return {
            "type": "ir.actions.act_window",
            "res_model": record._name,
            "views": [[record.get_formview_id(), "form"]],
            "res_id": record.id,
        }

    def reject_assign_document(self):
        self.filtered(lambda r: r.state == "pending").write(self._deleted_values())
