# Copyright 2023 Tecnativa - Víctor Martínez
# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sign OCA",
    "version": "13.0.1.0.0",
    "category": "Sign",
    "website": "https://github.com/OCA/server-ux",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["mail"],
    "data": [
        "data/sequence_data.xml",
        "security/sign_oca_security.xml",
        "security/ir.model.access.csv",
        "views/sign_request_views.xml",
        "views/menus.xml",
        "wizard/wizard_sign_request_views.xml",
    ],
    "demo": ["demo/ir_attachment_demo.xml"],
    "installable": True,
    "application": True,
    "maintainers": ["victoralmau"],
}
