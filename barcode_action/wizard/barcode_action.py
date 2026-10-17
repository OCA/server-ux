from odoo import fields, models


class BarcodeAction(models.TransientModel):
    _name = "barcode.action"
    _description = "Barcode Action"

    model = fields.Char(required=True)
    res_id = fields.Integer()
    method = fields.Char(required=True)
    state = fields.Selection(
        [("waiting", "Waiting"), ("warning", "Warning")], default="waiting"
    )
    status = fields.Text(default="Start scanning")
    # barcodes.barcode_events_mixin was removed in 20.0: the field is only
    # used to host the action_barcode_handler widget in the form view
    _barcode_scanned = fields.Char(
        "Barcode Scanned", help="Value of the last barcode scanned.", store=False
    )
