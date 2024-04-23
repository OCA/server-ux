# Copyright 2024 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Base Filter Default All Users",
    "summary": "Allows to set default filters for all users.",
    "version": "16.0.1.0.0",
    "category": "Tools",
    "website": "https://github.com/OCA/server-ux",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["base"],
    "data": [
        "security/groups.xml",
    ],
    "maintainers": ["ForgeFlow"],
    "assets": {
        "web.assets_backend": [
            "base_filter_default_all_user/static/src/search/"
            "favorite_menu/custom_favorite_item.js",
        ],
        "web.qunit_suite_tests": [
            "base_filter_default_all_user/static/tests/custom_favorite_item_tests.js"
        ],
    },
}
