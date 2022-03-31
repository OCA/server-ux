# Copyright 2015-2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class IrExports(models.Model):
    _inherit = "ir.exports"

    name = fields.Char(required=True)
    resource = fields.Char(readonly=True, help="Model's technical name.")
    model_id = fields.Many2one(
        "ir.model",
        "Model",
        store=True,
        inverse="_inverse_model_id",
        compute="_compute_model_id",
        domain=[("transient", "=", False)],
        help="Database model to export.",
    )

    @api.onchange("resource")
    def _onchange_resource(self):
        self.ensure_one()
        self.export_fields = [(5, 0, 0)]

    @api.depends("model_id")
    def _inverse_model_id(self):
        """Gets resource from model"""
        for record in self:
            record.resource = self.model_id.model

    @api.depends("resource")
    def _compute_model_id(self):
        """Gets resource from model"""
        IrModel = self.env["ir.model"]
        for record in self:
            record.model_id = IrModel._get(record.resource)

    @api.model_create_multi
    def create(self, vals_list):
        """Check required values when creating the record.

        Odoo's export dialog populates ``resource``, while this module's new
        form populates ``model_id``. At least one of them is required to
        trigger the methods that fill up the other, so this should fail if
        one is missing.
        """
        for vals in vals_list:
            if not any(f in vals for f in ("model_id", "resource")):
                raise ValidationError(_("You must supply a model or resource."))
        return super().create(vals_list)
