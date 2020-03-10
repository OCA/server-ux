# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import binascii
import json
import re

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class DocumentQuickAccessRule(models.Model):
    _name = "document.quick.access.rule"
    _description = "Document Quick Access Rule"
    _order = "priority,model_id"

    name = fields.Char(required=True)
    priority = fields.Integer(default=16, required=True)
    barcode_format = fields.Selection(
        [("standard", "Standard"), ("b64_standard", "Base64")],
        required=True,
        default="standard",
    )
    # All formats must have a function to determine the code from a record and
    # get the record from the code
    model_id = fields.Many2one("ir.model", required=True)
    active = fields.Boolean(default=True)

    def get_code(self, record):
        self.ensure_one()
        return getattr(self, "_get_code_%s" % self.barcode_format)(record)

    def _get_code_b64_standard(self, record):
        return base64.b64encode(self._get_code_standard(record).encode("utf-8")).decode(
            "utf-8"
        )

    def _get_code_standard(self, record):
        return "{},{}".format(record._name, record.id)

    def _check_code_b64_standard(self, code):
        try:
            aux_code = base64.b64decode(code.encode("utf-8"), validate=True)
        except binascii.Error:
            return False
        return self._check_code_standard(aux_code.decode("utf-8"))

    def _check_code_standard(self, code):
        return re.match("^[a-zA-Z0-9\\.]*,[0-9]*$", code)

    def _read_code_b64_standard(self, code):
        aux_code = base64.b64decode(code.encode("utf-8")).decode("utf-8")
        return self._read_code_standard(aux_code)

    def _read_code_standard(self, code):
        params = code.split(",")
        return self.env[params[0]].browse(int(params[1])).exists()

    def read_code_action(self, code):
        try:
            record = self.read_code(code)
        except UserError:
            return {
                "type": "ir.actions.act_window",
                "name": "Search QR",
                "res_model": "barcode.action",
                "views": [[False, "form"]],
                "target": "new",
                "context": json.dumps(
                    {
                        "default_model": "document.quick.access.rule",
                        "default_method": "read_code_action",
                        "default_state": "warning",
                        "default_status": _("Document cannot be found"),
                    }
                ),
            }
        record.check_access_rights("read")
        result = {
            "type": "ir.actions.act_window",
            "res_model": record._name,
            "views": [[record.get_formview_id(), "form"]],
            "res_id": record.id,
            "target": "main",
        }
        return result

    @api.model
    def read_code(self, code):
        formats = self._fields["barcode_format"].selection
        for barcode_format, _format_name in formats:
            if getattr(self, "_check_code_%s" % barcode_format)(code):
                record = getattr(self, "_read_code_%s" % barcode_format)(code)
                if record and self.search(
                    [
                        ("model_id.model", "=", record._name),
                        ("barcode_format", "=", barcode_format),
                    ]
                ):
                    return record
        raise UserError(_("No format has been found for this record"))
