# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Chained Swapper",
    "summary": "Chained Swapper",
    "version": "12.0.1.0.1",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "category": "Tools",
    "website": "https://github.com/OCA/server-ux",
    "license": "AGPL-3",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/chained_swapper_views.xml",
        "wizard/chained_swapper_wizard_views.xml",
    ],
    "demo": ["demo/chained_swapper_demo.xml",],
    "uninstall_hook": "uninstall_hook",
}
