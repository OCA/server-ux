# Copyright 2022 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Announcement",
    "version": "16.0.1.0.0",
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
        "views/announcement_tag_views.xml",
        "wizards/read_announcement_wizard.xml",
    ],
    "demo": [
        "demo/announcement_tag_demo.xml",
    ],
    "assets": {
        "web.assets_backend": [
            # "announcement/static/src/js/systray_service.js",
            # "announcement/static/src/js/models/**/*",
            # "announcement/static/src/js/announcement_menu_view/**/*",
            # "announcement/static/src/js/announcement_menu_container/**/*",
            "announcement/static/src/js/announcement_service/**/*",
            "announcement/static/src/js/announcement_menu/**/*",
        ],
    },
}
