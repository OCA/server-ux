# Copyright 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MassEditing(models.Model):
    _name = "mass.editing"
    _inherit = "mass.operation.mixin"
    _description = "Mass Editing"

    _wizard_model_name = "mass.editing.wizard"

    line_ids = fields.One2many(
        comodel_name="mass.editing.line", inverse_name="mass_editing_id"
    )
    apply_domain_in_lines = fields.Boolean(
        string="Apply domain in lines", compute="_compute_apply_domain_in_lines"
    )

    @api.depends("line_ids")
    def _compute_apply_domain_in_lines(self):
        for record in self:
            record.apply_domain_in_lines = any(record.line_ids.mapped("apply_domain"))
