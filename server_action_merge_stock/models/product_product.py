# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from openupgradelib.openupgrade import logged_query
from psycopg2.extensions import AsIs

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _server_action_merge_convert_fields(self):
        """Return the models and fields to convert before merging products"""
        return (
            ("product.supplierinfo", "product_id", ["min_qty"]),
            ("stock.production.lot", "product_id", ["product_qty"]),
            ("stock.quant", "product_id", ["quantity", "reserved_quantity"]),
            ("stock.valuation.layer", "product_id", ["quantity"]),
        )

    def _server_action_merge_coerce_fields(self):
        """
        Return the models and fields to coerce to the target product's UoM before
        merging products
        """
        return (
            ("account.analytic.line", "product_id", "product_uom_id"),
            ("account.move.line", "product_id", "product_uom_id"),
            ("contract.line", "product_id", "uom_id"),
            ("contract.template.line", "product_id", "uom_id"),
            ("hr.expense", "product_id", "product_uom_id"),
            ("mrp.bom", "product_id", "product_uom_id"),
            ("mrp.bom.line", "product_id", "product_uom_id"),
            ("mrp.bom.byproduct", "product_id", "product_uom_id"),
            ("mrp.production", "product_id", "product_uom_id"),
            ("mrp.unbuild", "product_id", "product_uom_id"),
            ("mrp.workorder", "product_id", "product_uom_id"),
            ("mrp.workorder.line", "product_id", "product_uom_id"),
            ("purchase.order.line", "product_id", "product_uom"),
            ("sale.order.line", "product_id", "product_uom"),
            ("sale.order.option", "product_id", "uom_id"),
            ("sale.order.template.line", "product_id", "product_uom_id"),
            ("sale.order.template.option", "product_id", "uom_id"),
            ("stock.inventory.line", "product_id", "product_uom_id"),
            ("stock.move", "product_id", "product_uom"),
            ("stock.move.line", "product_id", "product_uom_id"),
            ("stock.scrap", "product_id", "product_uom_id"),
        )

    def _server_action_merge_pre(self, records, action):
        """
        Convert UoMs in quants and supplierinfo records as they refer to the product's
        standard UoM.
        If UoM categories differ, coerce all quantities to the target product's default UoM
        """
        to_convert = records.filtered(lambda x: x.uom_id != self.uom_id)
        for product in to_convert:
            if product.uom_id.category_id != self.uom_id.category_id:
                product._server_action_merge_coerce(self.uom_id)
            else:
                product._server_action_merge_convert(self.uom_id)

    def _server_action_merge_convert(self, to_uom):
        """Convert quantities to the target UoM"""
        self.ensure_one()
        for (
            model,
            product_field,
            fields_list,
        ) in self._server_action_merge_convert_fields():
            if model not in self.env:
                continue
            for record in (
                self.env[model]
                .with_context(active_test=False)
                .search([(product_field, "=", self.id)])
            ):
                vals = {
                    field: self.uom_id._compute_quantity(record[field], to_uom)
                    for field in fields_list
                }
                record.write(vals)

    def _server_action_merge_coerce(self, to_uom):
        """Coerce UoMs from other categories than to_uom to the target UoM"""
        self.ensure_one()
        # TODO would it make sense to ie convert dozens to 12 units before coersion to m?
        for (
            model,
            product_field,
            uom_field,
        ) in self._server_action_merge_coerce_fields():
            if model not in self.env:
                continue
            logged_query(
                self.env.cr,
                """
                update %(table)s set %(uom_field)s=%(target_uom_id)s
                where %(product_field)s=%(product_id)s
                and %(uom_field)s in %(coerce_uom_ids)s
                """,
                {
                    "table": AsIs(self.env[model]._table),
                    "uom_field": AsIs(uom_field),
                    "target_uom_id": to_uom.id,
                    "product_field": AsIs(product_field),
                    "product_id": self.id,
                    "coerce_uom_ids": tuple(
                        to_uom.with_context(active_test=False)
                        .search([("category_id", "!=", to_uom.category_id.id)])
                        .ids
                    ),
                },
            )
