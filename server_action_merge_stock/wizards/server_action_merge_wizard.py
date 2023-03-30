# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import api, fields, models


class ServerActionMergeWizard(models.TransientModel):
    _inherit = "server.action.merge.wizard"

    product_uom_different_factor = fields.Boolean(compute="_compute_product_uom_flags")
    product_uom_different_category = fields.Boolean(
        compute="_compute_product_uom_flags"
    )

    @api.depends("target_line_id", "line_ids")
    def _compute_product_uom_flags(self):
        """
        Set flags to show warnings about potential inconsistencies resulting
        from the merge
        """
        for this in self:
            if (
                this.model_id.model not in ("product.product", "product.template")
                or not this.target_line_id
            ):
                this.update(
                    {
                        "product_uom_different_category": False,
                        "product_uom_different_factor": False,
                    }
                )
                continue
            source_products = sum(
                (this.line_ids - this.target_line_id).mapped("record"),
                self.env[this.model_id.model],
            )
            this.product_uom_different_category = (
                source_products.mapped("uom_id.category_id")
                != this.target_line_id.record.uom_id.category_id
            )
            this.product_uom_different_factor = set(
                source_products.mapped("uom_id.factor")
            ) != {this.target_line_id.record.uom_id.factor}
