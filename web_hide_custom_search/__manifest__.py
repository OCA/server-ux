# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Web Hide Custom Search",
    "summary": "Control visibility of custom filter and group-by options",
    "category": "Usability",
    "version": "15.0.1.0.0",
    "author": "Quartile, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-ux",
    "license": "AGPL-3",
    "depends": ["web"],
    "data": [
        "views/ir_model_views.xml",
        "views/res_groups_views.xml",
    ],
    "assets": {
        "web.assets_qweb": [
            "web_hide_custom_search/static/src/xml/*.xml",
        ],
        "web.assets_backend": [
            "web_hide_custom_search/static/src/js/*.esm.js",
        ],
        "web.qunit_suite_tests": [
            "web_hide_custom_search/static/tests/*.esm.js",
        ],
    },
    "maintainers": ["yostashiro", "aungkokolin1997"],
    "installable": True,
}
