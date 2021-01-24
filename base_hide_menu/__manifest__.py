# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Base Hide Menu",
    "summary": """
        This module allows a user to choose which Menus are displayed and
        which are not""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-ux",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/base_hide_menu_views.xml",
        "views/menuitem.xml",
    ],
}
