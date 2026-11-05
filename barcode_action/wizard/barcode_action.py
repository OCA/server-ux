from odoo import fields, models


class BarcodeAction(models.TransientModel):
    _name = "barcode.action"
    _description = "Barcode Action"

    # The `barcodes.barcode_events_mixin` abstract model was removed from core
    # in 20.0. Only its `_barcode_scanned` pseudo-field was used here, as the
    # anchor the `action_barcode_handler` widget binds to, so it is declared
    # directly on the wizard.
    _barcode_scanned = fields.Char(
        string="Barcode Scanned",
        store=False,
        help="Value of the last barcode scanned.",
    )

    model = fields.Char(required=True)
    res_id = fields.Integer()
    method = fields.Char(required=True)
    state = fields.Selection(
        [("waiting", "Waiting"), ("warning", "Warning")], default="waiting"
    )
    status = fields.Text(default="Start scanning")
