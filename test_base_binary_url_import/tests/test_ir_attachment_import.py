# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import base64
import io

import responses

from odoo.exceptions import AccessError, UserError
from odoo.modules.module import get_resource_path
from odoo.tests.common import Form, TransactionCase


class TestIrAttachmentImport(TransactionCase):
    def setUp(self, *args, **kwargs):
        super().setUp()
        # Test by database ID
        self.demo_record_1 = self.env["ir.attachment"].create(
            {"name": "Demo1", "type": "binary"}
        )
        self.demo_record_2 = self.env["ir.attachment"].create(
            {"name": "Demo2", "type": "binary"}
        )
        self.demo_url1 = "https://www.example.com/test.txt"
        self.demo_url2 = "https://www.example.com/test.pdf"
        self.demo_url3 = "http://httpbin.org/status/404"
        self.copy_paste_text = "%s,%s\n%s,%s" % (
            self.demo_record_1.id,
            self.demo_url1,
            self.demo_record_2.id,
            self.demo_url2,
        )
        self.copy_paste_text_wrong = "%s,%s\n%s,%s" % (
            0,
            self.demo_url1,
            0,
            self.demo_url2,
        )
        self.copy_paste_text_wrong_duplicate = "%s,%s\n%s,%s" % (
            self.demo_record_1.id,
            self.demo_url1,
            self.demo_record_1.id,
            self.demo_url2,
        )
        # Test by xml ID
        self.xml_demo_record_1 = self.env.ref(
            "test_base_binary_url_import.demo_attachment_01"
        )
        self.xml_demo_record_2 = self.env.ref(
            "test_base_binary_url_import.demo_attachment_02"
        )
        self.xml_copy_paste_text = "%s,%s\n%s,%s" % (
            "test_base_binary_url_import.demo_attachment_01",
            self.demo_url1,
            "test_base_binary_url_import.demo_attachment_02",
            self.demo_url2,
        )

        self.xml_copy_paste_text_wrong = "%s,%s\n%s,%s" % (
            "test_base_binary_url_import.demo_attachment_01_wrong",
            self.demo_url1,
            "test_base_binary_url_import.demo_attachment_02_wrong",
            self.demo_url2,
        )

        self.xml_copy_paste_text_wrong02 = "%s,%s\n%s,%s" % (
            "demo_attachment_01",
            self.demo_url1,
            "demo_attachment_01",
            self.demo_url2,
        )

        self.xml_copy_paste_text_wrong_duplicate = "%s,%s\n%s,%s" % (
            "test_base_binary_url_import.demo_attachment_01",
            self.demo_url1,
            "test_base_binary_url_import.demo_attachment_01",
            self.demo_url2,
        )

        self.xml_id_copy_paste_text_wrong = "%s,%s" % (
            "test_base_binary_url_import.demo_attachment_01",
            self.demo_url1,
        )

        self.ir_attachment_ir_model = self.env["ir.model"].search(
            [("model", "=", "ir.attachment")]
        )
        self.ir_attachment_file_ir_model_fields = self.env["ir.model.fields"].search(
            [("model_id", "=", self.ir_attachment_ir_model.id), ("name", "=", "datas")]
        )
        self.ir_attachment_filename_ir_model_fields = self.env[
            "ir.model.fields"
        ].search(
            [
                ("model_id", "=", self.ir_attachment_ir_model.id),
                ("name", "=", "name"),
            ]
        )

        self.wrong_ir_model = self.env["ir.model"].search([("model", "=", "res.users")])

    @responses.activate
    def test_wizard_import_database_id(self):
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
        wizard_form.target_model_id = self.ir_attachment_ir_model
        wizard_form.target_binary_field_id = self.ir_attachment_file_ir_model_fields
        wizard_form.target_binary_filename_field_id = (
            self.ir_attachment_filename_ir_model_fields
        )
        with wizard_form.line_ids.new() as line_form:
            line_form.binary_url_to_import = self.copy_paste_text
        wizard = wizard_form.save()
        self.assertFalse(self.demo_record_1.datas)
        self.assertEqual(self.demo_record_1.name, "Demo1")
        self.assertFalse(self.demo_record_2.datas)
        self.assertEqual(self.demo_record_2.name, "Demo2")
        # test not admin access error
        with self.assertRaises(AccessError):
            demo_user = self.env.ref("base.user_demo")
            wizard.with_user(demo_user).action_import_lines()

        wizard.action_import_lines()
        self.assertEqual(
            base64.b64decode(self.demo_record_1.datas), txt_binary.getvalue()
        )
        self.assertEqual(self.demo_record_1.name, "test.txt")
        self.assertEqual(
            base64.b64decode(self.demo_record_2.datas), pdf_binary.getvalue()
        )
        self.assertEqual(self.demo_record_2.name, "test.pdf")

    @responses.activate
    def test_wizard_import_xml_id(self):
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
        wizard_form.target_model_id = self.ir_attachment_ir_model
        wizard_form.target_binary_field_id = self.ir_attachment_file_ir_model_fields
        wizard_form.target_binary_filename_field_id = (
            self.ir_attachment_filename_ir_model_fields
        )
        with wizard_form.line_ids.new() as line_form:
            line_form.binary_url_to_import = self.xml_copy_paste_text
        wizard = wizard_form.save()
        self.assertFalse(self.xml_demo_record_1.datas)
        self.assertEqual(self.xml_demo_record_1.name, "XML Demo1")
        self.assertFalse(self.xml_demo_record_2.datas)
        self.assertEqual(self.xml_demo_record_2.name, "XML Demo2")
        # test not admin access error
        with self.assertRaises(AccessError):
            demo_user = self.env.ref("base.user_demo")
            wizard.with_user(demo_user).action_import_lines()

        wizard.action_import_lines()
        self.assertEqual(
            base64.b64decode(self.xml_demo_record_1.datas), txt_binary.getvalue()
        )
        self.assertEqual(self.xml_demo_record_1.name, "test.txt")
        self.assertEqual(
            base64.b64decode(self.xml_demo_record_2.datas), pdf_binary.getvalue()
        )
        self.assertEqual(self.xml_demo_record_2.name, "test.pdf")

    @responses.activate
    def test_wizard_import_wrong(self):
        # Wrong model
        wizard_form = Form(self.env["base.binary.url.import"])
        wizard_form.target_model_id = self.wrong_ir_model
        with self.assertRaises(UserError) as error_catcher:
            with wizard_form.line_ids.new() as line_form:
                line_form.binary_url_to_import = self.xml_copy_paste_text
        self.assertTrue("instead of model" in error_catcher.exception.args[0])
        # Wrong xml id
        wizard_form = Form(self.env["base.binary.url.import"])
        wizard_form.target_model_id = self.ir_attachment_ir_model
        with self.assertRaises(UserError) as error_catcher:
            with wizard_form.line_ids.new() as line_form:
                line_form.binary_url_to_import = self.xml_copy_paste_text_wrong
        self.assertTrue("XML ID" in error_catcher.exception.args[0])
        # Wrong xml id 02
        wizard_form = Form(self.env["base.binary.url.import"])
        wizard_form.target_model_id = self.ir_attachment_ir_model
        with self.assertRaises(UserError) as error_catcher:
            with wizard_form.line_ids.new() as line_form:
                line_form.binary_url_to_import = self.xml_copy_paste_text_wrong02
        self.assertTrue("is not an Integer or XMLID" in error_catcher.exception.args[0])
        # Wrong duplicate xml id
        wizard_form = Form(self.env["base.binary.url.import"])
        wizard_form.target_model_id = self.ir_attachment_ir_model
        with self.assertRaises(UserError) as error_catcher:
            with wizard_form.line_ids.new() as line_form:
                line_form.binary_url_to_import = (
                    self.xml_copy_paste_text_wrong_duplicate
                )
        self.assertTrue("Same XML IDs" in error_catcher.exception.args[0])
        # Wrong DB ID
        wizard_form = Form(self.env["base.binary.url.import"])
        wizard_form.target_model_id = self.ir_attachment_ir_model
        with self.assertRaises(UserError) as error_catcher:
            with wizard_form.line_ids.new() as line_form:
                line_form.binary_url_to_import = self.copy_paste_text_wrong
        self.assertTrue("IDs" in error_catcher.exception.args[0])
        # Wrong Duplicate DB ID
        wizard_form = Form(self.env["base.binary.url.import"])
        wizard_form.target_model_id = self.ir_attachment_ir_model
        with self.assertRaises(UserError) as error_catcher:
            with wizard_form.line_ids.new() as line_form:
                line_form.binary_url_to_import = self.copy_paste_text_wrong_duplicate
        self.assertTrue("Same database IDs" in error_catcher.exception.args[0])
        # Wrong target_record_identifier and no request session
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
        wizard_form = Form(self.env["base.binary.url.import"])
        wizard_form.target_model_id = self.ir_attachment_ir_model
        wizard_form.target_binary_field_id = self.ir_attachment_file_ir_model_fields
        wizard_form.target_binary_filename_field_id = (
            self.ir_attachment_filename_ir_model_fields
        )
        wizard_form.target_model_id = self.ir_attachment_ir_model
        with wizard_form.line_ids.new() as line_form:
            line_form.binary_url_to_import = self.xml_id_copy_paste_text_wrong
        wizard = wizard_form.save()
        for line in wizard.line_ids:
            self.assertEqual(line.target_record_identifier, False)
            self.assertFalse(self.xml_demo_record_1.datas)
            self.assertEqual(self.xml_demo_record_1.name, "XML Demo1")
            line_vals = line_form.binary_url_to_import.split(",")
            if not line.target_record_identifier and len(line_vals) == 2:
                line.write(
                    {
                        "target_record_identifier": line_vals[0],
                        "binary_url_to_import": line_vals[1],
                    }
                )

            line.import_binary_from_url()
            wizard.action_import_lines()
            self.assertEqual(
                base64.b64decode(self.xml_demo_record_1.datas), txt_binary.getvalue()
            )
            self.assertEqual(self.xml_demo_record_1.name, "test.txt")
