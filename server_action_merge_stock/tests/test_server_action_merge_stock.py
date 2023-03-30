# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo.tests.common import TransactionCase


class TestServerActionMerge(TransactionCase):
    def setUp(self):
        super().setUp()

        self.target_product = self.env["product.product"].create(
            {"name": "target", "uom_id": self.env.ref("uom.product_uom_unit").id}
        )
        self.source_product_dozen = self.env["product.product"].create(
            {
                "name": "source with UoM dozen",
                "type": "product",
                "uom_id": self.env.ref("uom.product_uom_dozen").id,
            }
        )
        self.source_product_meter = self.env["product.product"].create(
            {
                "name": "source with UoM m",
                "type": "product",
                "uom_id": self.env.ref("uom.product_uom_meter").id,
                "uom_po_id": self.env.ref("uom.product_uom_meter").id,
            }
        )
        self.quant = self.env["stock.quant"].create(
            {
                "product_id": self.source_product_dozen.id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "quantity": 1,
            }
        )
        self.inventory = self.env["stock.inventory"].create(
            {
                "name": "Inventory",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.source_product_meter.id,
                            "product_uom_id": self.env.ref("uom.product_uom_meter").id,
                            "location_id": self.env["stock.location"]
                            .search([], limit=1)
                            .id,
                        },
                    ),
                ],
            }
        )

    def test_product_merge(self):
        """Test we can merge products"""
        self.env["server.action.merge.wizard"]._merge_records(
            self.target_product, self.source_product_dozen + self.source_product_meter,
        )
        self.quant.invalidate_cache()
        self.inventory.invalidate_cache()
        self.assertEqual(self.quant.quantity, 12)
        self.assertEqual(
            self.inventory.line_ids.product_uom_id, self.env.ref("uom.product_uom_unit")
        )

    def test_uom_merge(self):
        """Test we can merge uoms"""
        self.env["server.action.merge.wizard"]._merge_records(
            self.env.ref("uom.product_uom_unit"),
            self.env.ref("uom.product_uom_dozen")
            + self.env.ref("uom.product_uom_meter"),
        )
        self.env.cache.invalidate()
        self.assertEqual(self.quant.quantity, 12)
        self.assertEqual(
            self.inventory.line_ids.product_uom_id, self.env.ref("uom.product_uom_unit")
        )
        self.assertEqual(
            self.source_product_meter.uom_po_id, self.env.ref("uom.product_uom_unit")
        )
