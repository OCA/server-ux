# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
from io import StringIO
import logging
import traceback
from .document_quick_access_rule import OCRException
from odoo import api, models

_logger = logging.getLogger(__name__)

try:
    from pyzbar.pyzbar import decode, ZBarSymbol
except (ImportError, IOError) as err:
    _logger.warning(err)
try:
    import pdf2image
    from pdf2image.exceptions import (
        PDFInfoNotInstalledError,
        PDFPageCountError,
        PDFSyntaxError
    )
except (ImportError, IOError) as err:
    _logger.warning(err)


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def _search_document_pdf(self):
        self.ensure_one()
        records = []
        try:
            images = pdf2image.convert_from_bytes(base64.b64decode(self.datas))
        except (
            PDFInfoNotInstalledError, PDFPageCountError, PDFSyntaxError
        ) as e:
            buff = StringIO()
            traceback.print_exc(file=buff)
            _logger.warning(buff.getvalue())
            raise OCRException(str(e))
        for im in images:
            records += self._search_pil_image(im)
        return records

    @api.model
    def _search_pil_image(self, image):
        results = decode(image, symbols=[ZBarSymbol.QRCODE])
        records = []
        rule_obj = self.env['document.quick.access.rule']
        for result in results:
            record = rule_obj.with_context(
                no_raise_document_access=True
            ).read_code(result.data.decode("utf-8"))
            if record and record not in records:
                records += record
        return records

    def _search_document(self):
        if self.mimetype == 'application/pdf':
            return self._search_document_pdf()
        return []

    def _process_quick_access_rules(self):
        self.ensure_one()
        results = self.env['ir.attachment']
        records = self._search_document()
        for record in records:
            if not results:
                result = self
                result.write({
                    'res_id': record.id,
                    'res_model': record._name
                })
            else:
                result = self.copy({
                    'res_id': record.id,
                    'res_model': record._name
                })
            results |= result
        return results or self
