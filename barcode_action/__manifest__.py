# Copyright 2017 Creu Blanca
# Copyright 2020 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Barcode action launcher",
    "version": "15.0.1.0.0",
    "category": "Extra Tools",
    "website": "https://github.com/OCA/server-ux",
    "author": "Creu Blanca, ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": "Allows to use barcodes as a launcher",
    "depends": ["barcodes"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/barcode_action_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "barcode_action/static/src/js/action_barcode_form.js",
            "barcode_action/static/src/js/action_barcode_widget.js",
        ],
    },
    "demo": ["demo/barcode_action_demo.xml"],
}
