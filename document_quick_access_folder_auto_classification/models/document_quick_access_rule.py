# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import api, models

try:
    from odoo.addons.queue_job.job import job
except ImportError:
    job = lambda *args, **kwargs: lambda func: func  # noqa: E731

_logger = logging.getLogger(__name__)


class DocumentQuickAccessRule(models.Model):
    _inherit = "document.quick.access.rule"

    @api.model
    def cron_folder_auto_classification(self, limit=None):
        backends = self.env["edi.backend"].search(
            [("backend_type_id.code", "=", "document_quick_access")]
        )
        new_limit = limit
        for backend in backends:
            new_limit = self._cron_folder_auto_classification(backend, new_limit)

    def _cron_folder_auto_classification_file(self, backend, file_data):
        exchange_record = backend.create_record(
            "document_quick_access",
            {
                "edi_exchange_state": "input_received",
                "exchange_file": backend.storage_id.get(file_data, binary=False),
                "exchange_filename": file_data,
            },
        )
        backend.storage_id.delete(file_data)
        backend.with_delay().exchange_process(exchange_record)
        return exchange_record

    def _cron_folder_auto_classification(self, backend, limit=None):
        if limit is not None and limit <= 0:
            return
        processed = 0
        storage = backend.storage_id
        for file_data in storage.list_files():
            if limit is not None and processed >= limit:
                break
            if self._cron_folder_auto_classification_file(backend, file_data):
                processed += 1
        if limit is None:
            return limit
        return limit - processed

    @api.model
    def read_code(self, code):
        try:
            return super().read_code(code)
        except Exception:
            if self.env.context.get("no_raise_document_access", False):
                return False
            raise
