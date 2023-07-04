# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Restrict records duplicating",
    "summary": "Adds a security group to restrict which users can copy records",
    "version": "15.0.1.0.1",
    "development_status": "Beta",
    "category": "Server tools",
    "website": "https://github.com/OCA/server-ux",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["chienandalu"],
    "license": "AGPL-3",
    "depends": ["web_tour"],
    "data": ["security/base_duplicate_security_group_security.xml"],
    "assets": {
        "web.assets_backend": [
            "/base_duplicate_security_group/static/src/js/duplicate.esm.js",
        ],
        "web.assets_tests": [
            "/base_duplicate_security_group/static/src/js/tour_duplicate.esm.js",
        ],
    },
}
