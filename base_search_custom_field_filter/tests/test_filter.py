# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from lxml import etree

from odoo import exceptions
from odoo.tests import Form, common


class TestFilter(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.custom_filter_model = cls.env["ir.ui.custom.field.filter"]
        cls.partner_model = cls.env.ref("base.model_res_partner")
        cls.record_1 = cls.custom_filter_model.create(
            {"name": "Phone", "expression": "phone", "model_id": cls.partner_model.id}
        )

    def test_1(self):
        arch = self.env["res.partner"].get_views([[False, "search"]])["views"][
            "search"
        ]["arch"]
        search = etree.fromstring(arch)
        self.assertTrue(
            search.xpath(
                """
                //search
                /field[@name="phone"]
            """
            )
        )

    def test_2(self):
        filter_form = Form(self.custom_filter_model)
        filter_form.model_id = self.partner_model
        filter_form.expression = "email"

        with self.assertRaises(exceptions.ValidationError):
            filter_form.name = "Phone"
            filter_form.save()

    def test_3(self):
        filter_form = Form(self.custom_filter_model)
        filter_form.model_id = self.partner_model
        filter_form.name = "Email"

        with self.assertRaises(exceptions.ValidationError):
            filter_form.expression = "phone"
            filter_form.save()

    def test_4(self):
        filter_form = Form(self.custom_filter_model)
        filter_form.model_id = self.partner_model
        filter_form.name = "Test Non Existance Field"

        with self.assertRaises(exceptions.ValidationError):
            filter_form.expression = "nonexistance_field"
            filter_form.save()

    def test_5(self):
        self.custom_filter_model.create(
            {
                "name": "City",
                "expression": "city",
                "model_id": self.partner_model.id,
                "position_after": "name",
            }
        )

        arch = self.env["res.partner"].get_views([[False, "search"]])["views"][
            "search"
        ]["arch"]
        search = etree.fromstring(arch)
        node = search.xpath("""
                //search
                /field[@name="city"]
            """)
        self.assertTrue(node)
        previous_node = node[0].getprevious()
        self.assertIsNotNone(previous_node)
        self.assertIn("name", previous_node.attrib)
        self.assertEqual(previous_node.attrib["name"], "name")
