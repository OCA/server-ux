# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, exceptions, fields, models


class IrUiCustomFilter(models.Model):
    _name = "ir.ui.custom.field.filter"
    _description = "Custom UI field filter"
    _order = "model_id, sequence, id"
    _sql_constraints = [
        (
            "unique_model_expression",
            "UNIQUE(model_id, expression)",
            "A filter with the same expression already exists for this model.",
        )
    ]

    sequence = fields.Integer()
    model_id = fields.Many2one(
        comodel_name="ir.model", required=True, ondelete="cascade"
    )
    model_name = fields.Char(
        related="model_id.model",
        store=True,
        readonly=True,
        index=True,
        string="Model name",
    )
    name = fields.Char(required=True, translate=True)
    expression = fields.Char(required=True)
    position_after = fields.Char(
        help="Optional field name for putting the filter after that one. "
        "If empty or not found, it will be put at the end.",
    )

    def _get_related_field(self):
        """Determine the chain of fields."""
        self.ensure_one()
        related = self.expression.split(".")
        target = self.env[self.model_name]
        for name in related:
            field = target._fields.get(name)
            target = target[name]
        return field

    @api.constrains("model_id", "expression")
    def _check_expression(self):
        """
        Validate that the expression refers to valid fields.

        This constraint ensures that the field expression can be resolved
        through the model's field chain. It attempts to traverse the field
        path and raises a validation error if any part of the path is invalid.
        """
        for record in self:
            try:
                record._get_related_field()
            except KeyError as e:
                raise exceptions.ValidationError(
                    _("Incorrect expression: %s.") % (str(e))
                ) from e

    @api.constrains("model_id", "name")
    def _check_name_unique(self):
        """
        Ensure filter names are unique per model.

        This constraint prevents creating multiple filters with the same name
        for the same model, which would cause confusion in the UI. It checks
        for existing filters with the same name and model, excluding the
        current record.
        """
        for record in self:
            domain = [
                ("model_id", "=", record.model_id.id),
                ("name", "=", record.name),
                ("id", "!=", record.id),
            ]
            if self.search_count(domain):
                raise exceptions.ValidationError(
                    _("A filter with the same name already exists for this model.")
                )
