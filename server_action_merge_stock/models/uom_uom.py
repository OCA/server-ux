# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import models


class UomUom(models.Model):
    _inherit = "uom.uom"

    def _server_action_merge_pre(self, records, action):
        """
        Convert quantities in quants and supplierinfo records as they refer to the product's
        standard UoM.
        If UoM categories differ, coerce all quantities to the target UoM
        """
        # lift off the uom conversion of procuts
        to_convert = self.env["product.product"].search(
            [
                (
                    "uom_id",
                    "in",
                    records.filtered(lambda x: x.category_id == self.category_id).ids,
                )
            ]
        )
        to_coerce = self.env["product.product"].search(
            [
                (
                    "uom_id",
                    "in",
                    records.filtered(lambda x: x.category_id != self.category_id).ids,
                )
            ]
        )
        for product in to_convert:
            product._server_action_merge_convert(self)
        for product in to_coerce:
            product._server_action_merge_coerce(self)
