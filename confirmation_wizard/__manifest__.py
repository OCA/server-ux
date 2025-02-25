# Copyright (C) 2024 Cetmix OÜ
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Confirmation Wizard",
    "summary": """
    This module adds a confirmation wizard that can be called with code.
    It does nothing by itself.
    """,
    "version": "16.0.1.0.0",
    "category": "Tools",
    "website": "https://github.com/OCA/server-ux",
    "author": "Cetmix, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/confirmation_wizard.xml",
    ],
}
