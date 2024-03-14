# © 2023 ForgeFlow, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

MAGIC_FIELDS = models.MAGIC_COLUMNS + [models.BaseModel.CONCURRENCY_CHECK_FIELD]


class FieldAccessRight(models.Model):
    _name = "field.access.right"
    _description = "Field Access Right"
    _order = "sequence"

    sequence = fields.Integer(default=10)
    model_id = fields.Many2one(
        "ir.model",
        string="Model",
        required=True,
        ondelete="cascade",
    )
    field_id = fields.Many2one(
        "ir.model.fields",
        string="Field",
        domain="""
                [
                    ("name", "not in", %s),
                    ("model_id", "=", model_id),
                ]
            """
        % str(MAGIC_FIELDS),
        ondelete="cascade",
        required=True,
    )
    readonly = fields.Selection([("yes", "Yes"), ("no", "No")])
    required = fields.Selection([("yes", "Yes"), ("no", "No")])
    invisible = fields.Selection([("yes", "Yes"), ("no", "No")])
    readonly_domain = fields.Char()
    required_domain = fields.Char()
    invisible_domain = fields.Char()
    exportable = fields.Selection([("yes", "Yes"), ("no", "No")])
    group_ids = fields.Many2many(string="Groups", comodel_name="res.groups")

    @api.onchange("model_id")
    def _onchange_model_id(self):
        self.field_id = False
