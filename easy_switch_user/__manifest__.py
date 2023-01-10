# Copyright 2018 Onestein
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Easy Switch User",
    "summary": """Lets administrators and developers quickly
    change user to test e.g. access rights""",
    "category": "Tools",
    "version": "15.0.1.0.0",
    "author": "Onestein, Vauxoo, Odoo Community Association (OCA)",
    "maintainers": [
        "luisg123v",
        "rolandojduartem",
    ],
    "website": "https://github.com/OCA/server-ux",
    "license": "AGPL-3",
    "depends": [
        "base",
    ],
    "assets": {
        "web.assets_tests": [
            "easy_switch_user/static/tests/tours/test_switch_user.js",
        ],
    },
    "data": [
        "views/res_users_views.xml",
    ],
    "installable": True,
}
