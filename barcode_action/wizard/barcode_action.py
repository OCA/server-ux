from odoo import fields, models


class BarcodeAction(models.TransientModel):
    _name = 'barcode.action'
    _inherit = "barcodes.barcode_events_mixin"

    model = fields.Char(
        required=True, readonly=True
    )
    res_id = fields.Integer()
    method = fields.Char(
        required=True, readonly=True
    )
    state = fields.Selection([
        ('waiting', 'Waiting'),
        ('warning', 'Warning')
    ], default='waiting', readonly=True, )
    status = fields.Text(
        readonly=True,
        default="Start scanning",
    )
