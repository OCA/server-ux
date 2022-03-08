# Copyright 2021 ForgeFlow, S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "User Role Analysis",
    "version": "13.0.1.0.0",
    "summary": "specific user role analysis reports",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-ux",
    "category": "Tools",
    "license": "LGPL-3",
    "depends": ["base_user_role", "board"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "report/user_role_reports.xml",
    ],
    "installable": True,
    "application": False,
}
