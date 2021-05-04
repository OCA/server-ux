# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Base Overdue Reminder",
    "version": "13.0.1.0.0",
    "category": "Tools",
    "license": "AGPL-3",
    "summary": "Base overdue reminder by mail/letter",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "maintainers": ["Saran440"],
    "website": "https://github.com/OCA/server-ux",
    "depends": ["base", "mail"],
    "data": ["security/ir.model.access.csv", "views/reminder_definition_view.xml"],
    "installable": True,
    "application": True,
}
