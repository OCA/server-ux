# Copyright 2020 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Base Menu Visibility Restriction",
    "version": "13.0.1.0.0",
    "category": "Extra Tools",
    "development_status": "Production/Stable",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "summary": "Restrict (with groups) menu visibilty",
    "website": "https://github.com/OCA/server-ux",
    "license": "AGPL-3",
    "depends": ["web_tour"],
    "maintainers": ["victoralmau"],
    "data": ["views/ir_ui_menu.xml"],
    "demo": ["demo/res_group.xml", "demo/ir_ui_menu.xml"],
    "installable": True,
}
