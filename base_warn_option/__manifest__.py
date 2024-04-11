# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{
    "name": "Base Warn Option",
    "summary": "Add Options to Warn Messages",
    "version": "15.0.1.0.0",
    "development_status": "Alpha",
    "category": "Tools",
    "website": "https://github.com/OCA/server-ux",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["Shide", "rafaelbn"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["base", "base_setup"],
    "data": [
        "security/ir.model.access.csv",
        "views/warn_option_views.xml",
        "views/res_config_settings_views.xml",
    ],
}
