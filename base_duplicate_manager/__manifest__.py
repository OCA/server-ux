# Copyright 2026 CIT Services
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Base Duplicate Manager",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "summary": "Restricts the Duplicate action per model based on Group access rights",
    "author": "CIT Services, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-ux",
    "license": "LGPL-3",
    "depends": ["base"],
    "data": ["views/ir_model_access.xml", "views/res_groups.xml"],
    "installable": True,
}
