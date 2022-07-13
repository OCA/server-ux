# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
import shutil
import uuid

from mock import patch

from odoo import tools
from odoo.tools import mute_logger

from odoo.addons.component.tests.common import TransactionComponentRegistryCase


class Encoded:
    __slots__ = "data"

    def __init__(self, data):
        self.data = data


class TestDocumentQuickAccessClassification(TransactionComponentRegistryCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context, tracking_disable=True, test_queue_job_no_delay=True
            )
        )

        self = cls
        self._setup_registry(self)
        self._load_module_components(self, "component_event")
        self._load_module_components(self, "edi")
        self._load_module_components(self, "edi_storage")
        self._load_module_components(
            self, "document_quick_access_folder_auto_classification"
        )
        self.base_dir = os.path.join(self.env["ir.attachment"]._filestore(), "storage")
        try:
            os.mkdir(self.base_dir)
            self.clean_base_dir = True
        except FileExistsError:
            # If the directory exists we respect it and do not clean it on teardown.
            self.clean_base_dir = False
        self.tmpdir = os.path.join(self.base_dir, str(uuid.uuid4()))
        self.storage = self.env["storage.backend"].create(
            {
                "name": "Demo Storage",
                "backend_type": "filesystem",
                "directory_path": self.tmpdir,
            }
        )
        self.backend = self.env["edi.backend"].create(
            {
                "name": "Demo Backend",
                "backend_type_id": self.env.ref(
                    "document_quick_access_folder_auto_classification.backend_type"
                ).id,
                "storage_id": self.storage.id,
            }
        )
        os.mkdir(self.tmpdir)
        self.model_id = self.env.ref("base.model_res_partner")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmpdir)
        if cls.clean_base_dir:
            shutil.rmtree(cls.base_dir)
        return super().tearDownClass()

    def test_ok_pdf_multi(self):
        partners = self.env["res.partner"].create({"name": "Partner 1"})
        partners |= self.env["res.partner"].create({"name": "Partner 2"})
        partners |= self.env["res.partner"].create({"name": "Partner 3"})
        partners |= self.env["res.partner"].create({"name": "Partner 4"})
        self.test_ok_pdf(partners)

    @mute_logger("odoo.addons.queue_job.models.base")
    def test_ok_pdf_multi_limit(self):
        """Limit the number of files to process"""
        partner = self.env["res.partner"].create({"name": "Partner 1"})
        self.env["document.quick.access.rule"].create(
            {
                "model_id": self.model_id.id,
                "name": "PARTNER",
                "priority": 1,
                "barcode_format": "standard",
            }
        )
        file = tools.file_open(
            "test_file.pdf",
            mode="rb",
            subdir="addons/document_quick_access_folder_auto_classification" "/tests",
        ).read()
        self.env["document.quick.access.rule"].create(
            {
                "model_id": self.model_id.id,
                "name": "PARTNER",
                "priority": 1,
                "barcode_format": "standard",
            }
        )
        with open(os.path.join(self.tmpdir, "test_file.pdf"), "wb") as f:
            f.write(file)
        with open(os.path.join(self.tmpdir, "test_file_2.pdf"), "wb") as f:
            f.write(file)
        code = [Encoded(partner.get_quick_access_code().encode("utf-8"))]
        files = os.listdir(self.tmpdir)
        self.assertEqual(2, len(files))
        with patch(
            "odoo.addons.document_quick_access_folder_auto_classification."
            "components.document_quick_access_process.decode"
        ) as ptch:
            ptch.return_value = code
            self.env["document.quick.access.rule"].with_context(
                ignore_process_path=True
            ).cron_folder_auto_classification(limit=1)
            ptch.assert_called_once()
        attachments = self.env["ir.attachment"].search(
            [("res_model", "=", partner._name), ("res_id", "=", partner.id)]
        )
        self.assertTrue(attachments)
        self.assertEqual(1, len(attachments))
        files = os.listdir(self.tmpdir)
        self.assertEqual(1, len(files))

    @mute_logger("odoo.addons.queue_job.models.base")
    def test_ok_pdf(self, partners=False):
        """Assign automatically PDFs to their assigned place"""
        if not partners:
            partners = self.env["res.partner"].create({"name": "Partner"})
        file = tools.file_open(
            "test_file.pdf",
            mode="rb",
            subdir="addons/document_quick_access_folder_auto_classification" "/tests",
        ).read()

        self.env["document.quick.access.rule"].create(
            {
                "model_id": self.model_id.id,
                "name": "PARTNER",
                "priority": 1,
                "barcode_format": "standard",
            }
        )
        with open(os.path.join(self.tmpdir, "test_file.pdf"), "wb") as f:
            f.write(file)
        code = [
            Encoded(partner.get_quick_access_code().encode("utf-8"))
            for partner in partners
        ]
        with patch(
            "odoo.addons.document_quick_access_folder_auto_classification."
            "components.document_quick_access_process.decode"
        ) as ptch:
            ptch.return_value = code
            self.env["document.quick.access.rule"].with_context(
                ignore_process_path=True
            ).cron_folder_auto_classification()
            ptch.assert_called()
        self.assertTrue(partners)
        for partner in partners:
            self.assertTrue(
                self.env["ir.attachment"].search(
                    [("res_model", "=", partner._name), ("res_id", "=", partner.id)]
                )
            )

    @mute_logger("odoo.addons.queue_job.models.base")
    def test_no_ok_assign(self):
        """Assign failed files"""
        file = tools.file_open(
            "test_file.pdf",
            mode="rb",
            subdir="addons/document_quick_access_folder_auto_classification/" "tests",
        ).read()
        with open(os.path.join(self.tmpdir, "test_file.pdf"), "wb") as f:
            f.write(file)
        self.env["document.quick.access.rule"].with_context(
            ignore_process_path=True
        ).cron_folder_auto_classification()
        self.assertTrue(
            self.env["edi.exchange.record"].search(
                [
                    ("backend_id", "=", self.backend.id),
                    ("exchange_filename", "=", "test_file.pdf"),
                    ("edi_exchange_state", "=", "input_processed_error"),
                ]
            )
        )
        partner = self.env["res.partner"].create({"name": "Partner"})
        missing = self.env["edi.exchange.record"].search(
            [
                ("exchange_filename", "=", "test_file.pdf"),
                ("edi_exchange_state", "=", "input_processed_error"),
                ("backend_id", "=", self.backend.id),
            ]
        )
        self.assertTrue(missing)
        action = missing.action_open_related_record()
        self.assertFalse(action.keys())
        self.env["document.quick.access.rule"].create(
            {
                "model_id": self.model_id.id,
                "name": "PARTNER",
                "priority": 1,
                "barcode_format": "standard",
            }
        )
        wizard = self.env["document.quick.access.missing.assign"].create(
            {
                "object_id": "{},{}".format(partner._name, partner.id),
                "exchange_record_id": missing.id,
            }
        )
        wizard.manually_assign()
        self.assertEqual(missing.edi_exchange_state, "input_processed")
        action = missing.action_open_related_record()
        self.assertEqual(partner._name, action["res_model"])
        self.assertEqual(partner.id, action["res_id"])

    @mute_logger("odoo.addons.queue_job.models.base")
    def test_failure(self):
        """We will check that if a major exception raises all is handled"""
        file = tools.file_open(
            "test_file.pdf",
            mode="rb",
            subdir="addons/document_quick_access_folder_auto_classification/" "tests",
        ).read()
        with open(os.path.join(self.tmpdir, "test_file.pdf"), "wb") as f:
            f.write(file)
        with self.assertRaises(TypeError):
            with patch(
                "odoo.addons.document_quick_access_folder_auto_classification."
                "components.document_quick_access_process.decode"
            ) as ptch:
                ptch.return_value = 1
                self.env["document.quick.access.rule"].with_context(
                    ignore_process_path=True
                ).cron_folder_auto_classification()

    @mute_logger("odoo.addons.queue_job.models.base")
    def test_no_ok_reject(self):
        """We will check that we can manage and reject failed files"""
        file = tools.file_open(
            "test_file.pdf",
            mode="rb",
            subdir="addons/document_quick_access_folder_auto_classification/" "tests",
        ).read()
        with open(os.path.join(self.tmpdir, "test_file.pdf"), "wb") as f:
            f.write(file)
        self.env["document.quick.access.rule"].with_context(
            ignore_process_path=True
        ).cron_folder_auto_classification()
        missing = self.env["edi.exchange.record"].search(
            [
                ("exchange_filename", "=", "test_file.pdf"),
                ("edi_exchange_state", "=", "input_processed_error"),
                ("backend_id", "=", self.backend.id),
            ]
        )
        self.assertTrue(missing)
        missing.with_context(
            document_quick_access_reject_file=True
        ).action_exchange_process()
        missing.refresh()
        self.assertEqual(missing.edi_exchange_state, "input_processed")
        self.assertFalse(missing.model)

    @mute_logger("odoo.addons.queue_job.models.base")
    def test_corrupted(self):
        """We will check that corrupted files are stored also"""
        file = tools.file_open(
            "test_file.pdf",
            mode="rb",
            subdir="addons/document_quick_access_folder_auto_classification/" "tests",
        ).read()
        with open(os.path.join(self.tmpdir, "test_file.pdf"), "wb") as f:
            f.write(file[: int(len(file) / 2)])
        with mute_logger(
            "odoo.addons.document_quick_access_folder_auto_classification."
            "components.document_quick_access_process",
        ):
            self.env["document.quick.access.rule"].with_context(
                ignore_process_path=True
            ).cron_folder_auto_classification()
        self.assertTrue(
            self.env["edi.exchange.record"].search(
                [
                    ("backend_id", "=", self.backend.id),
                    ("exchange_filename", "=", "test_file.pdf"),
                    ("edi_exchange_state", "=", "input_processed_error"),
                ]
            )
        )
