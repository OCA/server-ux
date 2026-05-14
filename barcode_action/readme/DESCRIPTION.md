This module allows you to use barcodes to launch Odoo actions.

When a barcode is scanned, the configured Python method is called with
the scanned value and is expected to return the action to execute next
(for example, opening the form view of the matching record).
