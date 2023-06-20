# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Base multi branch company",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "category": "base",
    "summary": "Add multi branch of company",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-ux",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_branch_view.xml",
        "views/res_company.xml",
    ],
    "installable": True,
    "maintainers": ["Saran440"],
}
