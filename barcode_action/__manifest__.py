# Copyright 2017 Creu Blanca
# Copyright 2020 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Barcode action launcher",
    "version": "19.0.1.0.0",
    "category": "Extra Tools",
    "website": "https://github.com/OCA/server-ux",
    "author": "Creu Blanca, ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": "Use barcode scans to launch Odoo actions",
    "depends": ["barcodes"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/barcode_action_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "barcode_action/static/src/js/action_barcode_widget.esm.js",
            "barcode_action/static/src/scss/action_barcode_widget.scss",
            "barcode_action/static/src/xml/action_barcode_widget.xml",
        ],
    },
    "demo": ["demo/barcode_action_demo.xml"],
}
