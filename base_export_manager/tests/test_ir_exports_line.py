# Copyright 2015 Antiun Ingenieria S.L. - Javier Iniesta
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestIrExportsLineCase(TransactionCase):
    def setUp(self):
        super(TestIrExportsLineCase, self).setUp()
        m_ir_exports = self.env["ir.exports"]
        self.export = m_ir_exports.create(
            {"name": "Partner Test", "resource": "res.partner"}
        )
        self.partner_model = self.env["ir.model"].search(
            [("model", "=", "res.partner")]
        )
        self.field_parent_id = self.env["ir.model.fields"].search(
            [("name", "=", "parent_id"), ("model_id", "=", self.partner_model.id)]
        )
        self.field_name = self.env["ir.model.fields"].search(
            [("name", "=", "name"), ("model_id", "=", self.partner_model.id)]
        )

    def _record_create(self, field_name):
        m_ir_exports_line = self.env["ir.exports.line"]
        virt_line = m_ir_exports_line.new(
            {"name": field_name, "export_id": self.export.id}
        )
        virt_line._inverse_name()
        return m_ir_exports_line.create(virt_line._convert_to_write(virt_line._cache))

    def test_check_name(self):
        self._record_create("name")
        with self.assertRaises(ValidationError):
            self._record_create("name")
        with self.assertRaises(ValidationError):
            self._record_create("bad_error_name")

    def test_get_label_string(self):
        export_line = self._record_create("parent_id/name")
        self.assertEqual(
            export_line.with_context(lang="en_US").label,
            "Related Company/Name (parent_id/name)",
        )
        with self.assertRaises(ValidationError):
            self._record_create("")

    def test_model_default_by_context(self):
        """Fields inherit the model_id by context."""
        m_ir_exports_line = self.env["ir.exports.line"]
        virt_line = m_ir_exports_line.new({"name": "name", "export_id": self.export.id})
        virt_line._inverse_name()
        line = m_ir_exports_line.with_context(
            default_model1_id=self.export.model_id.id
        ).create(virt_line._convert_to_write(virt_line._cache))
        self.assertEqual(line.model1_id, self.export.model_id)

    def test_inverse_name(self):
        line = self._record_create("parent_id/parent_id/parent_id/name")
        self.assertEqual(line.model1_id, self.partner_model)
        self.assertEqual(line.model2_id, self.partner_model)
        self.assertEqual(line.field1_id, self.field_parent_id)
        self.assertEqual(line.field2_id, self.field_parent_id)
        self.assertEqual(line.field3_id, self.field_parent_id)
        self.assertEqual(line.field4_id, self.field_name)

    def test_name_validation(self):
        with self.assertRaises(ValidationError):
            self._record_create("parent_id/parent_id/parent_id/name/parent_id")

    def test_compute_name(self):
        line = self.env["ir.exports.line"].create(
            {
                "export_id": self.export.id,
                "field1_id": self.field_parent_id.id,
                "field2_id": self.field_parent_id.id,
                "field3_id": self.field_parent_id.id,
                "field4_id": self.field_name.id,
            }
        )
        self.assertEqual(line.name, "parent_id/parent_id/parent_id/name")

    def test_write_name_same_root(self):
        self._record_create("parent_id")
        line = self._record_create("name")
        # This should end without errors
        line.name = "parent_id/name"
