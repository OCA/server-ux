# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Test Base Binary URL Import",
    "summary": "Unittests for Base Binary URL Import module",
    "version": "16.0.1.0.1",
    "development_status": "Alpha",
    "category": "Uncategorized",
    "website": "https://github.com/OCA/server-ux",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "depends": ["base_binary_url_import"],
    "data": ["security/ir.model.access.csv", "views/test_binary.xml"],
    "demo": [
        "demo/demo_test_binary.xml",
        "demo/ir_attachment.xml",
    ],
    "external_dependencies": {"python": ["responses"]},
}
