# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from lxml import etree

from odoo import exceptions
from odoo.tests import Form, common


class TestFilter(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_1(self):
        filter_form = Form(self.env["ir.ui.custom.field.filter"])
        filter_form.model_id = self.env.ref("base.model_res_partner")
        filter_form.name = "Title"
        with self.assertRaises(exceptions.ValidationError):
            filter_form.expression = "title_1"
            filter_form.save()

        filter_form.expression = "title"
        filter_form.save()
        arch = self.env["res.partner"].get_view(False, "search")["arch"]
        search = etree.fromstring(arch)
        self.assertTrue(
            search.xpath(
                """
            //search
            /field[@name="title"]
        """
            )
        )
