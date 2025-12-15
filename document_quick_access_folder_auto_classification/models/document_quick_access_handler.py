import base64
import logging
import traceback
from io import StringIO

from odoo import _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    from pyzbar.pyzbar import ZBarSymbol, decode
except (OSError, ImportError) as err:
    _logger.warning(err)
try:
    import pdf2image
    from pdf2image.exceptions import (
        PDFInfoNotInstalledError,
        PDFPageCountError,
        PDFSyntaxError,
    )
except (OSError, ImportError) as err:
    _logger.warning(err)
try:
    import cv2
    import numpy
except (OSError, ImportError):
    cv2 = False


class EdiDocumentQuickAccessHandler(models.AbstractModel):
    _name = "document.quick.access.handler"
    _inherit = [
        "edi.oca.handler.process",
    ]
    _description = "Component Handler for Document Quick Access"

    def process(self, exchange_record):
        data = exchange_record.exchange_file
        records = self._search_document_pdf(data)
        for record in records:
            self.env["ir.attachment"].create(
                self._get_attachment_vals(record, exchange_record)
            )
        if records:
            record = records[0]
            exchange_record.write({"res_id": record.id, "model": record._name})
        elif self.env.context.get("document_quick_access_reject_file"):
            return
        else:
            raise UserError(_("No file found"))

    def _get_attachment_vals(self, record, exchange_record):
        return {
            "name": exchange_record.exchange_filename,
            "datas": exchange_record.exchange_file,
            "res_id": record.id,
            "res_model": record._name,
        }

    def _search_document_pdf(self, datas):
        if self.env.context.get("document_quick_access_reject_file"):
            return []
        if self.env.context.get("force_object_process"):
            return [self.env.context["force_object_process"]]
        records = []
        try:
            images = pdf2image.convert_from_bytes(base64.b64decode(datas))
        except (PDFInfoNotInstalledError, PDFPageCountError, PDFSyntaxError) as e:
            buff = StringIO()
            traceback.print_exc(file=buff)
            _logger.warning(buff.getvalue())
            raise UserError(str(e)) from e
        for im in images:
            records += self._search_pil_image(im)
        return records

    def _search_pil_image(self, image):
        zbar_results = decode(image, symbols=[ZBarSymbol.QRCODE])
        results = [zbar_result.data.decode("utf-8") for zbar_result in zbar_results]
        if not results and cv2:
            detector = cv2.QRCodeDetector()
            is_ok, cv2_results, _vertices, _binary = detector.detectAndDecodeMulti(
                numpy.asarray(image)
            )
            if is_ok:
                results = cv2_results
        records = []
        rule_obj = self.env["document.quick.access.rule"]
        for result in results:
            record = rule_obj.with_context(no_raise_document_access=True).read_code(
                result
            )
            if record and record not in records:
                records += record
        return records
