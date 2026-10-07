# Copyright 2026 CIT Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Base Import Manager",
    "summary": "Manage Import Access per Group",
    "category": "Tools",
    "version": "18.0.1.0.0",
    "depends": ["base_import"],
    "website": "https://github.com/OCA/server-ux",
    "author": "CIT Services, Odoo Community Association (OCA)",
    "data": [
        "views/ir_model_access.xml",
        "views/res_groups.xml",
    ],
    "installable": True,
    "application": False,
    "license": "AGPL-3",
}
