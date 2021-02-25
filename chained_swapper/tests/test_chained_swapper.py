# Copyright 2020 Tecnativa - Ernesto Tejeda
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import exceptions
from odoo.modules import registry
from odoo.tests import common

from ..hooks import uninstall_hook


class TestChainedSwapper(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestChainedSwapper, cls).setUpClass()
        cls.env["res.lang"].load_lang("es_ES")
        res_partner = cls.env["res.partner"]
        cls.partner_parent = res_partner.create(
            {"name": "parent partner cs", "lang": "en_US"}
        )
        cls.partner_child_1 = res_partner.create(
            {"name": "partner child1 cs", "parent_id": cls.partner_parent.id}
        )
        cls.partner_child_2 = res_partner.create(
            {"name": "partner child2 cs", "parent_id": cls.partner_parent.id}
        )
        product_product = cls.env["product.product"]
        cls.product_category = cls.env.ref("product.product_category_all")
        cls.categ_parent = product_product.create(
            {"name": "parent categ", "categ_id": cls.product_category.id}
        )
        cls.categ = product_product.create(
            {"name": "parent template categ", "categ_id": cls.categ_parent.categ_id.id}
        )
        # Prevent duplicate error removing demo data if exists
        record = cls.env.ref("chained_swapper.chained_swapper_demo", False)
        if record:
            record.unlink()
        cls.chained_swapper = cls.env["chained.swapper"].create(
            {
                "name": "Language",
                "model_id": cls.env.ref("base.model_res_partner").id,
                "field_id": cls.env.ref("base.field_res_partner__lang").id,
                "sub_field_ids": [(0, 0, {"sub_field_chain": "child_ids.lang"})],
                "constraint_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Only parent company",
                            "expression": "bool(records.mapped('parent_id'))",
                        },
                    )
                ],
            }
        )
        cls.chained_swapper.add_action()
        cls.chained_swapper_inherits = cls.env["chained.swapper"].create(
            {
                "name": "Product",
                "model_id": cls.env.ref("product.model_product_product").id,
                "field_id": cls.env.ref(
                    "product.field_product_product__product_tmpl_id"
                ).id,
            }
        )
        cls.chained_swapper_many2one = cls.env["chained.swapper"].create(
            {
                "name": "Language",
                "model_id": cls.env.ref("product.model_product_product").id,
                "field_id": cls.env.ref("product.field_product_product__categ_id").id,
                "sub_field_ids": [
                    (0, 0, {"sub_field_chain": "product_tmpl_id.categ_id"})
                ],
            }
        )
        cls.chained_swapper.add_action()

    def test_create_unlink_action(self):
        """Test if Sidebar Action is added / removed to / from given object."""
        action = (
            self.chained_swapper.ref_ir_act_window_id
            and self.chained_swapper.ref_ir_act_window_id.binding_model_id
        )
        self.assertTrue(action)
        # Remove the action
        self.chained_swapper.unlink_action()
        action = self.chained_swapper.ref_ir_act_window_id
        self.assertFalse(action)
        # Add an action
        self.chained_swapper.add_action()
        action = (
            self.chained_swapper.ref_ir_act_window_id
            and self.chained_swapper.ref_ir_act_window_id.binding_model_id
        )
        self.assertTrue(action)

    def test_unlink_chained_swapper(self):
        """Test if related actions are removed when a chained swapper
        record is unlinked."""
        action_id = self.chained_swapper.ref_ir_act_window_id.id
        self.chained_swapper.unlink()
        action = self.env["ir.actions.act_window"].search([("id", "=", action_id)])
        self.assertFalse(action)

    def test_change_constrained_partner_language(self):
        with self.assertRaises(exceptions.UserError):
            self.env["chained.swapper.wizard"].with_context(
                active_model="res.partner",
                active_id=self.partner_parent.id,
                active_ids=(self.partner_parent | self.partner_child_1).ids,
                chained_swapper_id=self.chained_swapper.id,
            ).create({"lang": "es_ES"})

    def test_change_partner_language(self):
        self.env["chained.swapper.wizard"].with_context(
            active_model="res.partner",
            active_id=self.partner_parent.id,
            active_ids=[self.partner_parent.id],
            chained_swapper_id=self.chained_swapper.id,
        ).create({"lang": "es_ES"})
        self.assertEqual(self.partner_parent.lang, "es_ES")
        self.assertEqual(self.partner_child_1.lang, "es_ES")
        self.assertEqual(self.partner_child_2.lang, "es_ES")

    def test_many2one(self):
        self.env["chained.swapper.wizard"].with_context(
            active_model="product.product",
            active_id=self.categ_parent.id,
            active_ids=[self.categ_parent.id],
            chained_swapper_id=self.chained_swapper_many2one.id,
        ).create({"categ_id": self.env.ref("product.product_category_all").id})
        self.assertEqual(
            self.categ_parent.categ_id.id,
            self.env.ref("product.product_category_all").id,
        )

    def test_change_action(self):
        res = (
            self.env["chained.swapper.wizard"]
            .with_context(
                active_model="res.partner",
                active_id=self.partner_parent.id,
                active_ids=[self.partner_parent.id],
                chained_swapper_id=self.chained_swapper.id,
            )
            .create({"lang": "en_US"})
        )
        self.assertEqual(res.change_action().get("type"), "ir.actions.act_window_close")

    def test_uninstall_hook(self):
        """Test if related actions are removed when mass editing
        record is uninstalled."""
        action_id = self.chained_swapper.ref_ir_act_window_id.id
        uninstall_hook(self.cr, registry)
        self.assertFalse(self.env["ir.actions.act_window"].browse(action_id).exists())

    def test_invalid_constraint(self):
        with self.assertRaises(exceptions.ValidationError):
            self.chained_swapper.constraint_ids.write(
                {"expression": "Something incorrect"}
            )

    def test_compute_allowed_field_ids(self):
        field_obj = self.env["ir.model.fields"]
        model_obj = self.env["ir.model"]
        self.chained_swapper_inherits._compute_allowed_field_ids()
        all_models = self.chained_swapper_inherits.model_id
        active_model_obj = self.env[self.chained_swapper_inherits.model_id.model]
        if active_model_obj._inherits:
            keys = list(active_model_obj._inherits.keys())
            all_models |= model_obj.search([("model", "in", keys)])
        recs = field_obj.search(
            [
                ("ttype", "not in", ["reference", "function", "one2many"]),
                ("model_id", "in", all_models.ids),
            ]
        )
        self.assertTrue(recs)

    def test_write(self):
        rec = self.chained_swapper.ref_ir_act_window_id.id
        rec_write = self.chained_swapper.write(
            {"ref_ir_act_window_id": rec, "name": "Language"}
        )
        self.assertTrue(rec_write)

    def test_check_sub_field_chain(self):
        with self.assertRaises(exceptions.ValidationError):
            self.chained_swapper.sub_field_ids.write(
                {"sub_field_chain": "Sub-field incompatible"}
            )

    def test_validation_check_sub_field_chain(self):
        with self.assertRaises(exceptions.ValidationError):
            self.chained_swapper.sub_field_ids.chained_swapper_id.write({"field_id": 1})

    def test_onchange_model_id(self):
        self.chained_swapper_inherits._onchange_model_id()
        self.chained_swapper_inherits.field_id = False
        self.assertFalse(self.chained_swapper_inherits.field_id)
