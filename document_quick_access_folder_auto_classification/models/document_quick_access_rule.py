# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import logging
import os
import shutil

from odoo import api, models
from odoo.modules.registry import Registry

try:
    from odoo.addons.queue_job.job import job
except ImportError:
    job = lambda *args, **kwargs: lambda func: func  # noqa: E731

_logger = logging.getLogger(__name__)


class OCRException(Exception):
    def __init__(self, name):
        self.name = name


class DocumentQuickAccessRule(models.Model):
    _inherit = "document.quick.access.rule"

    @api.model
    def cron_folder_auto_classification(
        self, path=False, processing_path=False, limit=False
    ):
        if not path:
            path = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param(
                    "document_quick_access_auto_classification.path", default=False
                )
            )
        if not path:
            return False
        if not processing_path and not self.env.context.get("ignore_process_path"):
            processing_path = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param(
                    "document_quick_access_auto_classification.process_path",
                    default=False,
                )
            )
        elements = [
            os.path.join(path, f)
            for f in os.listdir(path)
            if os.path.isfile(os.path.join(path, f))
        ]
        if limit:
            elements = elements[:limit]
        for element in elements:
            obj = self
            new_element = element
            if processing_path:
                new_cr = Registry(self.env.cr.dbname).cursor()
            try:
                if processing_path:
                    new_element = os.path.join(
                        processing_path, os.path.basename(element)
                    )
                    shutil.copy(element, new_element)
                    obj = (
                        api.Environment(new_cr, self.env.uid, self.env.context)[
                            self._name
                        ]
                        .browse()
                        .with_delay(**self._delay_vals())
                    )
                obj._process_document(new_element)
                if processing_path:
                    new_cr.commit()
            except Exception:
                if processing_path:
                    os.unlink(new_element)
                    new_cr.rollback()
                raise
            finally:
                if processing_path:
                    new_cr.close()
            if processing_path:
                os.unlink(element)
        return True

    @api.model
    def _delay_vals(self):
        return {}

    @api.model
    def process_document(self, filename, datas):
        attachment = self.env["ir.attachment"].create(
            self._get_attachment_vals(filename, datas)
        )
        return attachment._process_quick_access_rules()

    @api.model
    @job(default_channel="root.document_quick_access_classification")
    def _process_document(self, element):
        try:
            filename = os.path.basename(element)
            datas = base64.b64encode(open(element, "rb").read())
            results = self.process_document(filename, datas)
            return self._postprocess_document(element, results)
        except OCRException:
            _logger.warning("Element %s was corrupted" % element)
            os.unlink(element)

    @api.model
    def _postprocess_document(self, path, results):
        filename = os.path.basename(path)
        if any(result.res_id for result in results):
            new_path = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param(
                    "document_quick_access_auto_classification.ok_path", default=False
                )
            )
        else:
            new_path = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param(
                    "document_quick_access_auto_classification.failure_path",
                    default=False,
                )
            )
            self.env["document.quick.access.missing"].create(
                {"name": filename, "attachment_id": results.id}
            )
        if new_path:
            shutil.copy(path, os.path.join(new_path, filename))
        os.unlink(path)
        return bool(results)

    def _get_attachment_vals(self, filename, datas):
        return {"name": filename, "datas": datas, "datas_fname": filename}

    @api.model
    def read_code(self, code):
        try:
            return super().read_code(code)
        except Exception:
            if self.env.context.get("no_raise_document_access", False):
                return False
            raise
