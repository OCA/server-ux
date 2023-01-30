from odoo import fields, models


class IrModelFields(models.Model):
    _inherit = "ir.model.fields"

    deprecated = fields.Boolean(help="Whether the field is deprecated or not.")

    def _reflect_field_params(self, field, model_id):
        result = super()._reflect_field_params(field, model_id)
        result["deprecated"] = bool(field.deprecated)
        return result
