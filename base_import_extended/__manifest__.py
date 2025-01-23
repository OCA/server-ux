# Copyright 2025 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Base import extended",
    "summary": "Base import extended to manage templates and extra conversion methods",
    "version": "17.0.1.0.0",
    "category": "Tools",
    "website": "https://github.com/OCA/server-ux",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "base_import",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/base_import_mapping_template_views.xml",
        "views/base_import_mapping_value_map_views.xml",
        # "views/invoice_import_xls_view.xml",
    ],
}
