# Copyright 2025 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Base Cancel Confirm Selection",
    "version": "18.0.1.0.0",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "category": "Usability",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/server-ux",
    "depends": ["base_cancel_confirm"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/cancel_confirm.xml",
        "views/cancel_reason_view.xml",
        "views/cancel_confirm_template.xml",
    ],
    "installable": True,
    "maintainers": ["Saran440"],
}
