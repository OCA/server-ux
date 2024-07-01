# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

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
        self.exchange_model = self.env["edi.exchange.record"]

        self._setup_registry(self)
        self._load_module_components(self, "component_event")
        self._load_module_components(self, "edi")
        self._load_module_components(
            self, "document_quick_access_folder_auto_classification"
        )
        self.backend = self.env["edi.backend"].create(
            {
                "name": "Demo Backend",
                "backend_type_id": self.env.ref(
                    "document_quick_access_folder_auto_classification.backend_type"
                ).id,
            }
        )
        self.model_id = self.env.ref("base.model_res_partner")

    def test_ok_pdf_multi(self):
        partners = self.env["res.partner"].create({"name": "Partner 1"})
        partners |= self.env["res.partner"].create({"name": "Partner 2"})
        partners |= self.env["res.partner"].create({"name": "Partner 3"})
        partners |= self.env["res.partner"].create({"name": "Partner 4"})
        self.test_ok_pdf(partners)

    @mute_logger("odoo.addons.queue_job.models.base")
    def test_ok_pdf(self, partners=False):
        """Assign automatically PDFs to their assigned place"""
        if not partners:
            partners = self.env["res.partner"].create({"name": "Partner"})
        file = tools.file_open(
            "addons/document_quick_access_folder_auto_classification/tests/test_file.pdf",
            mode="rb",
        ).read()

        self.env["document.quick.access.rule"].create(
            {
                "model_id": self.model_id.id,
                "name": "PARTNER",
                "priority": 1,
                "barcode_format": "standard",
            }
        )
        code = [
            Encoded(partner.get_quick_access_code().encode("utf-8"))
            for partner in partners
        ]
        with patch(
            "odoo.addons.document_quick_access_folder_auto_classification."
            "components.document_quick_access_process.decode"
        ) as ptch:
            ptch.return_value = code
            self.backend.create_record(
                "document_quick_access",
                {
                    "exchange_filename": "test_file.pdf",
                    "exchange_file": base64.b64encode(file),
                    "edi_exchange_state": "input_received",
                },
            )
            self.backend._cron_check_input_exchange_sync()
            self.assertEqual(ptch.call_count, 1)
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
            "addons/document_quick_access_folder_auto_classification/tests/test_file.pdf",
            mode="rb",
        ).read()
        self.backend.create_record(
            "document_quick_access",
            {
                "exchange_filename": "test_file.pdf",
                "exchange_file": base64.b64encode(file),
                "edi_exchange_state": "input_received",
            },
        )
        self.backend._cron_check_input_exchange_sync()
        self.assertTrue(
            self.exchange_model.search(
                [
                    ("backend_id", "=", self.backend.id),
                    ("exchange_filename", "=", "test_file.pdf"),
                    ("edi_exchange_state", "=", "input_processed_error"),
                ]
            )
        )
        partner = self.env["res.partner"].create({"name": "Partner"})
        missing = self.exchange_model.search(
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
            "addons/document_quick_access_folder_auto_classification/tests/test_file.pdf",
            mode="rb",
        ).read()
        with self.assertRaises(TypeError):
            with patch(
                "odoo.addons.document_quick_access_folder_auto_classification."
                "components.document_quick_access_process.decode"
            ) as ptch:
                ptch.return_value = 1
                self.backend.create_record(
                    "document_quick_access",
                    {
                        "exchange_filename": "test_file.pdf",
                        "exchange_file": base64.b64encode(file),
                        "edi_exchange_state": "input_received",
                    },
                )
                self.backend._cron_check_input_exchange_sync()

    @mute_logger("odoo.addons.queue_job.models.base")
    def test_no_ok_reject(self):
        """We will check that we can manage and reject failed files"""
        file = tools.file_open(
            "addons/document_quick_access_folder_auto_classification/tests/test_file.pdf",
            mode="rb",
        ).read()
        self.backend.create_record(
            "document_quick_access",
            {
                "exchange_filename": "test_file.pdf",
                "exchange_file": base64.b64encode(file),
                "edi_exchange_state": "input_received",
            },
        )
        self.backend._cron_check_input_exchange_sync()
        missing = self.exchange_model.search(
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
            "document_quick_access_folder_auto_classification/tests/test_file.pdf",
            mode="rb",
        ).read()
        with mute_logger(
            "odoo.addons.document_quick_access_folder_auto_classification."
            "components.document_quick_access_process",
        ):
            self.backend.create_record(
                "document_quick_access",
                {
                    "exchange_filename": "test_file.pdf",
                    "exchange_file": base64.b64encode(file[: int(len(file) / 2)]),
                    "edi_exchange_state": "input_received",
                },
            )
            self.backend._cron_check_input_exchange_sync()
        self.assertTrue(
            self.exchange_model.search(
                [
                    ("backend_id", "=", self.backend.id),
                    ("exchange_filename", "=", "test_file.pdf"),
                    ("edi_exchange_state", "=", "input_processed_error"),
                ]
            )
        )
