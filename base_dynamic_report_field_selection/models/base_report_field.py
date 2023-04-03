from odoo import api, fields, models


class BaseReportField(models.AbstractModel):
    _name = "base.report.field"
    _description = "Base Report Field"

    sequence = fields.Integer(default=10)
    field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        domain=lambda self: self._domain_field_id(),
    )

    @api.model
    def _domain_field_id(self):
        model_id = self.env["ir.model"]._get_id(self._name)
        return [("model_id", "=", model_id)]
