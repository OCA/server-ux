# Copyright 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MassEditing(models.Model):
    _name = "mass.editing"
    _inherit = "mass.operation.mixin"
    _description = "Mass Editing"

    _wizard_model_name = "mass.editing.wizard"

    line_ids = fields.One2many(
        comodel_name="mass.editing.line", inverse_name="mass_editing_id"
    )
