# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "Live UI updates",
    "summary": "Base module for live UI updates",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Technical",
    "website": "https://github.com/OCA/server-ux",
    "author": "Hunki Enterprises BV, Odoo Community Association (OCA)",
    "maintainers": ["hbrunn"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "bus",
        "web",
    ],
    "demo": [
        "demo/live_update_notification.xml",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/live_update_notification.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/base_live_update/static/src/*.js",
        ],
        "web.qunit_suite_tests": [],
    },
}
