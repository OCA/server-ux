# Copyright 2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Date Range Account",
    "version": "15.0.1.0.0",
    "category": "Accounting",
    "license": "AGPL-3",
    "summary": "Add Date Range menu entry in Invoicing app",
    "author": "Akretion,Odoo Community Association (OCA)",
    "maintainers": ["alexis-via"],
    "website": "https://github.com/OCA/server-ux",
    "depends": ["account", "date_range"],
    "data": [
        "views/date_range.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "auto_install": True,
}
