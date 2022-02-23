# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Base Cancel Confirm",
    "version": "15.0.1.0.3",
    "author": "Ecosoft,Odoo Community Association (OCA)",
    "category": "Usability",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/server-ux",
    "depends": ["base"],
    "data": [
        "wizard/cancel_confirm.xml",
        "security/ir.model.access.csv",
        "templates/cancel_confirm_template.xml",
    ],
    "auto_install": False,
    "installable": True,
    "maintainers": ["kittiu"],
}
