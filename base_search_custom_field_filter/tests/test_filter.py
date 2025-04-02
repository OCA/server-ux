# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from lxml import etree

from odoo import exceptions
from odoo.exceptions import ValidationError
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestFilter(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model = cls.env["res.partner"]
        cls.custom_filter_model = cls.env["ir.ui.custom.field.filter"]

    def test_00(self):
        filter_form = Form(self.custom_filter_model)
        filter_form.model_id = self.env.ref("base.model_res_partner")
        filter_form.name = "Title"

        with self.assertRaises(exceptions.ValidationError):
            filter_form.expression = "title_1"
            filter_form.save()
        filter_form.expression = "title"
        filter_form.save()
        arch = self.model.get_view(False, "search")["arch"]
        search = etree.fromstring(arch)
        self.assertTrue(search.xpath("//search/field[@name='title']"))

    def test_01_invalid_expression(self):
        filter_form = Form(self.custom_filter_model)
        filter_form.model_id = self.env.ref("base.model_res_partner")
        filter_form.name = "Invalid Expression"
        with self.assertRaises(exceptions.ValidationError):
            filter_form.expression = "invalid_field"
            filter_form.save()

    def test_02_valid_expression(self):
        filter_form = Form(self.custom_filter_model)
        filter_form.model_id = self.env.ref("base.model_res_partner")
        filter_form.name = "Valid Expression"
        filter_form.expression = "name"
        filter_form.save()
        arch = self.model.get_view(False, "search")["arch"]
        search = etree.fromstring(arch)
        self.assertTrue(search.xpath("//search/field[@name='name']"))

    def test_03_duplicate_filter(self):
        self.env["ir.ui.custom.field.filter"].create(
            {
                "model_id": self.env.ref("base.model_res_partner").id,
                "name": "Duplicate Filter",
                "expression": "name",
            }
        )
        with self.assertRaises(ValidationError):
            self.env["ir.ui.custom.field.filter"].create(
                {
                    "model_id": self.env.ref("base.model_res_partner").id,
                    "name": "Duplicate Filter",
                    "expression": "email",
                }
            )

    def test_04_add_custom_filters(self):
        res = {"arch": "<search><field name='email'/></search>"}
        custom_filters = [
            self.custom_filter_model.create(
                {
                    "model_id": self.env.ref("base.model_res_partner").id,
                    "name": "Custom Name",
                    "expression": "name",
                    "position_after": "email",
                }
            ),
            self.custom_filter_model.create(
                {
                    "model_id": self.env.ref("base.model_res_partner").id,
                    "name": "Custom Phone",
                    "expression": "phone",
                    "position_after": "",
                }
            ),
        ]
        res = self.model._add_custom_filters(res, custom_filters)
        arch = etree.fromstring(res["arch"])
        email_field = arch.xpath("//field[@name='email']")
        self.assertTrue(email_field)
        next_field = email_field[0].getnext()
        self.assertEqual(next_field.get("name"), "name")
        last_field = arch.xpath("//field[last()]")
        self.assertTrue(last_field)
        self.assertEqual(last_field[0].get("name"), "phone")

    def test_05_get_views_with_custom_filter(self):
        self.custom_filter_model.create(
            {
                "model_id": self.env.ref("base.model_res_partner").id,
                "name": "Custom Name",
                "expression": "name",
            }
        )
        res = self.env["res.partner"].get_views([], {})
        self.assertIn("name", res["models"]["res.partner"])
        self.assertFalse(res["models"]["res.partner"]["name"]["selectable"])

    def test_06_invalid_related_field(self):
        with self.assertRaises(ValidationError):
            self.custom_filter_model.create(
                {
                    "model_id": self.env.ref("base.model_res_partner").id,
                    "name": "Invalid Field",
                    "expression": "non_existent_field",
                }
            )
