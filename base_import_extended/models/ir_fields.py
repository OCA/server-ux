# Copyright 2025 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import ormcache


class IrFieldsConverter(models.AbstractModel):
    _inherit = "ir.fields.converter"

    @api.model
    @ormcache("model", "field", "subfield", "value")
    def cached_db_id_for(self, model, field, subfield, value):
        res_id, field_type, warnings = self.with_context(
            use_cached_db_id_for=False
        ).db_id_for(model, field, subfield, value)
        return res_id, field_type, warnings

    @api.model
    def db_id_for(self, model, field, subfield, value):
        if self.env.context.get("use_cached_db_id_for", False):
            return self.cached_db_id_for(model, field, subfield, value)
        return super().db_id_for(model, field, subfield, value)
