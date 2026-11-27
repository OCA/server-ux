from lxml import etree

from odoo.tests import TransactionCase

from ..models.base import PARAM


class TestModule(TransactionCase):
    def _limits(self):
        view = self.env.ref("base.view_model_form")
        arch = self.env["ir.model"].get_view(view_id=view.id, view_type="form")["arch"]
        return etree.fromstring(arch).xpath("//field[@name='field_id']/list/@limit")

    def test_limit(self):
        self.env["ir.config_parameter"].set_int(PARAM, 200)
        self.assertEqual(self._limits(), ["200"])

    def test_no_limit(self):
        # no value: the web client default applies
        self.env["ir.config_parameter"].set_int(PARAM, 0)
        self.assertEqual(self._limits(), [])
