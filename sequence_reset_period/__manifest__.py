# Copyright (C) 2017 Creu Blanca
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Reset Sequences on selected period ranges",
    "version": "11.0.1.0.0",
    "category": "Reporting",
    "website": "https://github.com/OCA/server-tools",
    "author": "Creu Blanca, "
              "Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "installable": True,
    "application": False,
    "summary": "Adds a check digit on sequences",
    "depends": [
        "base",
    ],
    "data": [
        "views/sequence_views.xml",
    ],
}
