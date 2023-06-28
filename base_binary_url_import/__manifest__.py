# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Base Binary URL Import",
    "summary": "Wizard to import binary files from URL on existing records",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Uncategorized",
    "website": "https://github.com/OCA/server-ux",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "depends": ["base", "base_import", "web_domain_field"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_config_parameter.xml",
        "wizard/base_binary_url_import_view.xml",
    ],
    "external_dependencies": {"python": ["pyrfc6266"]},
}
