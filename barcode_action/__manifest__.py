# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Barcode action launcher",
    "version": "12.0.1.0.0",
    "category": "Extra Tools",
    "website": "https://github.com/OCA/server-ux",
    "author": "Creu Blanca, Eficent, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": "Allows to use barcodes as a launcher",
    "depends": ["barcodes"],
    "data": ["views/barcode_templates.xml", "wizard/barcode_action_view.xml"],
    "demo": ["demo/barcode_action_demo.xml"],
}
