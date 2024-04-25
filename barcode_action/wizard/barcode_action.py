from odoo import fields, models


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
