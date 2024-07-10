# Copyright 2024 Moduon Team (https://www.moduon.team)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models

from .tier_validation import BASE_EXCEPTION_FIELDS


class TierValidationException(models.Model):
    _name = "tier.validation.exception"
    _description = "Tier Validation Exceptions"
    _rec_name = "model_name"

    @api.model
    def _get_tier_validation_model_names(self):
        return self.env["tier.definition"]._get_tier_validation_model_names()

    model_id = fields.Many2one(
        comodel_name="ir.model",
        string="Model",
        required=True,
        ondelete="cascade",
        domain=lambda self: [("model", "in", self._get_tier_validation_model_names())],
    )
    model_name = fields.Char(
        related="model_id.model",
        string="Model",
        store=True,
        readonly=True,
        index=True,
    )
    field_ids = fields.Many2many(
        comodel_name="ir.model.fields",
        string="Fields",
        domain="[('id', 'in', valid_model_field_ids)]",
        required=True,
    )
    valid_model_field_ids = fields.One2many(
        comodel_name="ir.model.fields",
        compute="_compute_valid_model_field_ids",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    allowed_to_write_under_validation = fields.Boolean(
        string="Write under Validation",
        default=True,
    )
    allowed_to_write_after_validation = fields.Boolean(
        string="Write after Validation",
        default=True,
    )

    @api.depends("model_id")
    def _compute_valid_model_field_ids(self):
        for record in self:
            record.valid_model_field_ids = (
                self.env["ir.model.fields"]
                .sudo()
                .search(
                    [
                        ("model", "=", record.model_name),
                        ("name", "not in", BASE_EXCEPTION_FIELDS),
                    ]
                )
            )

    @api.constrains(
        "allowed_to_write_under_validation", "allowed_to_write_after_validation"
    )
    def _check_allowed_to_write(self):
        if (
            not self.allowed_to_write_under_validation
            and not self.allowed_to_write_after_validation
        ):
            raise exceptions.ValidationError(
                _(
                    "At least one of these fields must be checked! "
                    "Write under Validation, Write after Validation"
                )
            )

    _sql_constraints = [
        (
            "model_company_under_after_unique",
            "unique(model_id, company_id, "
            "allowed_to_write_under_validation, allowed_to_write_after_validation)",
            _(
                "The model already exists for this company with this "
                "Write Validation configuration!"
            ),
        )
    ]
