# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Archive Security",
    "summary": "Archive/unarchive security feature",
    "version": "16.0.1.0.0",
    "author": "Camptocamp, Italo LOPES, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "category": "Others",
    "depends": ["base"],
    "data": [
        "security/res_groups.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "base_archive_security/static/src/js/*.js",
        ],
    },
    "website": "https://github.com/OCA/server-ux",
    "installable": True,
}
