# Copyright 2022 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Announcement",
    "version": "13.0.1.0.0",
    "summary": "Notify internal users about relevant organization stuff",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Server UX",
    "website": "https://github.com/OCA/server-ux",
    "depends": ["mail"],
    "data": [
        "security/announcement_security.xml",
        "security/ir.model.access.csv",
        "views/announcement_views.xml",
        "wizards/read_announcement_wizard.xml",
        "templates/assets_backend.xml",
    ],
    "qweb": [
        "static/src/xml/announcement_dialog.xml",
        "static/src/xml/announcement.xml",
    ],
    "installable": True,
}
