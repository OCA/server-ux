# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import base64
import io
import json
from contextlib import contextmanager

import responses

from odoo.exceptions import UserError
from odoo.modules.module import get_resource_path
from odoo.tests.common import Form, TransactionCase


class TestBinaryURLImport(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.demo_xmlid = "test_base_binary_url_import.test_binary_demo"
        cls.demo_record_xmlid = cls.env.ref(cls.demo_xmlid)
        cls.demo_record = cls.env["test.binary"].create({"name": "Demo"})
        cls.demo_url1 = "https://www.example.com/test.txt"
        cls.demo_url2 = "https://www.example.com/test.pdf"
        cls.copy_paste_text = "%s,%s\n%s,%s" % (
            cls.demo_xmlid,
            cls.demo_url1,
            cls.demo_record.id,
            cls.demo_url2,
        )
        cls.test_binary_ir_model = cls.env["ir.model"].search(
            [("model", "=", "test.binary")]
        )
        cls.test_binary_file_ir_model_fields = cls.env["ir.model.fields"].search(
            [("model_id", "=", cls.test_binary_ir_model.id), ("name", "=", "file")]
        )
        cls.test_binary_filename_ir_model_fields = cls.env["ir.model.fields"].search(
            [
                ("model_id", "=", cls.test_binary_ir_model.id),
                ("name", "=", "file_name"),
            ]
        )

    @contextmanager
    def yield_wizard_form(self):
        with Form(self.env["base.binary.url.import"]) as wizard_form:
            wizard_form.target_model_id = self.test_binary_ir_model
            wizard_form.target_binary_field_id = self.test_binary_file_ir_model_fields
            yield wizard_form

    def test_wizard_computation(self):
        with Form(self.env["base.binary.url.import"]) as wizard_form:
            wizard_form.target_model_id = self.test_binary_ir_model
            self.assertEqual(
                wizard_form.target_binary_field_domain,
                json.dumps(
                    [
                        ("ttype", "=", "binary"),
                        ("model_id", "=", wizard_form.target_model_id.id),
                    ]
                ),
            )
            self.assertEqual(
                wizard_form.target_binary_filename_field_domain,
                json.dumps(
                    [
                        ("ttype", "=", "char"),
                        ("model_id", "=", wizard_form.target_model_id.id),
                    ]
                ),
            )
            wizard_form.target_binary_field_id = self.test_binary_file_ir_model_fields
            with wizard_form.line_ids.new() as line_form:
                self.assertFalse(line_form.is_target_record_identifier_required)
                line_form.binary_url_to_import = self.demo_url1
                self.assertTrue(line_form.is_target_record_identifier_required)
                line_form.target_record_identifier = self.demo_xmlid

    def test_wizard_onchange_lines(self):
        with self.yield_wizard_form() as wizard_form:
            with wizard_form.line_ids.new() as line_form:
                line_form.binary_url_to_import = self.copy_paste_text
            self.assertEqual(len(wizard_form.line_ids), 2)
            line_ids_records_dicts = wizard_form.line_ids._records
            self.assertEqual(
                line_ids_records_dicts[0].get("target_record_identifier"),
                self.demo_xmlid,
            )
            self.assertEqual(
                line_ids_records_dicts[0].get("binary_url_to_import"), self.demo_url1
            )
            self.assertEqual(
                line_ids_records_dicts[1].get("target_record_identifier"),
                str(self.demo_record.id),
            )
            self.assertEqual(
                line_ids_records_dicts[1].get("binary_url_to_import"), self.demo_url2
            )

    def test_wizard_sanity_check(self):
        with self.yield_wizard_form() as wizard_form:
            with self.assertRaises(UserError):
                with wizard_form.line_ids.new() as line_form:
                    # Two same XMLIDs
                    line_form.binary_url_to_import = "%s,%s\n%s,%s" % (
                        self.demo_xmlid,
                        self.demo_url1,
                        self.demo_xmlid,
                        self.demo_url2,
                    )
        with self.yield_wizard_form() as wizard_form:
            with self.assertRaises(UserError):
                with wizard_form.line_ids.new() as line_form:
                    # Two same DB IDs
                    line_form.binary_url_to_import = "%s,%s\n%s,%s" % (
                        self.demo_record.id,
                        self.demo_url1,
                        self.demo_record.id,
                        self.demo_url2,
                    )
        with self.yield_wizard_form() as wizard_form:
            with self.assertRaises(UserError):
                with wizard_form.line_ids.new() as line_form:
                    # XML ID and DB ID for same record
                    line_form.binary_url_to_import = "%s,%s\n%s,%s" % (
                        self.demo_xmlid,
                        self.demo_url1,
                        self.demo_record_xmlid.id,
                        self.demo_url2,
                    )
        with self.yield_wizard_form() as wizard_form:
            with self.assertRaises(UserError):
                with wizard_form.line_ids.new() as line_form:
                    # Unexisting DB ID
                    line_form.binary_url_to_import = "%s,%s\n%s,%s" % (
                        self.demo_xmlid,
                        self.demo_url1,
                        self.demo_record.id + 1,
                        self.demo_url2,
                    )
        with self.yield_wizard_form() as wizard_form:
            with self.assertRaises(UserError):
                with wizard_form.line_ids.new() as line_form:
                    # Unexisting XML ID
                    line_form.binary_url_to_import = "%s,%s\n%s,%s" % (
                        "base_binary_url_import.unexisting_xmlid",
                        self.demo_url1,
                        self.demo_record_xmlid.id,
                        self.demo_url2,
                    )
        with self.yield_wizard_form() as wizard_form:
            with self.assertRaises(UserError):
                with wizard_form.line_ids.new() as line_form:
                    # XML ID from different model
                    line_form.binary_url_to_import = "%s,%s\n%s,%s" % (
                        "base.partner_demo",
                        self.demo_url1,
                        self.demo_record_xmlid.id,
                        self.demo_url2,
                    )

    @responses.activate
    def test_wizard_import(self):
        txt_binary = io.BytesIO()
        txt_file_path = get_resource_path(
            "test_base_binary_url_import", "tests", "files", "test.txt"
        )
        with open(txt_file_path, "rb") as txt_file:
            txt_binary.write(txt_file.read())
        responses.add(
            responses.GET,
            self.demo_url1,
            body=txt_binary.getvalue(),
            status=200,
            content_type="text/plain",
        )
        pdf_binary = io.BytesIO()
        pdf_file_path = get_resource_path(
            "test_base_binary_url_import", "tests", "files", "test.pdf"
        )
        with open(pdf_file_path, "rb") as pdf_file:
            pdf_binary.write(pdf_file.read())
        responses.add(
            responses.GET,
            self.demo_url2,
            body=pdf_binary.getvalue(),
            status=200,
            content_type="application/pdf",
        )
        wizard_form = Form(self.env["base.binary.url.import"])
        wizard_form.target_model_id = self.test_binary_ir_model
        wizard_form.target_binary_field_id = self.test_binary_file_ir_model_fields
        wizard_form.target_binary_filename_field_id = (
            self.test_binary_filename_ir_model_fields
        )
        with wizard_form.line_ids.new() as line_form:
            line_form.binary_url_to_import = self.copy_paste_text
        wizard = wizard_form.save()
        self.assertFalse(self.demo_record_xmlid.file)
        self.assertFalse(self.demo_record_xmlid.file_name)
        self.assertFalse(self.demo_record.file)
        self.assertFalse(self.demo_record.file_name)
        wizard.action_import_lines()
        self.assertEqual(
            base64.b64decode(self.demo_record_xmlid.file), txt_binary.getvalue()
        )
        self.assertEqual(self.demo_record_xmlid.file_name, "test.txt")
        self.assertEqual(base64.b64decode(self.demo_record.file), pdf_binary.getvalue())
        self.assertEqual(self.demo_record.file_name, "test.pdf")
