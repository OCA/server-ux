# Copyright 2026 CIT Services
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Base Report Manager",
    "summary": "Manage report actions visibility per user group",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "author": "CIT Services, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-ux",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["base"],
    "data": [
        "views/res_groups_views.xml",
    ],
}
