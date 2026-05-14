from odoo import api, fields, models
from odoo.exceptions import ValidationError


class BarcodeAction(models.TransientModel):
    _name = "barcode.action"
    _inherit = "barcodes.barcode_events_mixin"
    _description = "Barcode Action"

    model = fields.Char(required=True)
    res_id = fields.Integer()
    method = fields.Char(required=True)
    state = fields.Selection(
        [("waiting", "Waiting"), ("warning", "Warning")], default="waiting"
    )
    status = fields.Text(default="Start scanning")

    @api.constrains("method")
    def _check_method_is_public(self):
        # The OWL widget calls the configured method through orm.call on
        # behalf of the user, so allowing dunder/private names would let
        # anyone with access to a barcode.action wizard invoke arbitrary
        # internal methods (e.g. ``unlink``, ``_compute_*``).
        for record in self:
            if record.method and record.method.startswith("_"):
                raise ValidationError(
                    self.env._(
                        "The barcode action method %(method)s is not allowed: "
                        "only public methods can be triggered from a barcode "
                        "scan.",
                        method=record.method,
                    )
                )
