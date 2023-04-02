from odoo import api, fields, models


class BaseReportField(models.AbstractModel):
    _name = "base.report.field"

    report_field_ids = fields.Many2many(
        comodel_name="ir.model.fields",
        domain=lambda self: self._domain_report_field_ids(),
    )

    @api.model
    def _domain_report_field_ids(self):
        model_id = self.env["ir.model"]._get_id(self._name)
        return [("model_id", "=", model_id)]
