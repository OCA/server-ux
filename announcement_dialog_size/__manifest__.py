# Copyright 2022 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Announcement Dialog Size",
    "version": "16.0.1.0.0",
    "summary": "Allow set announcement dialogs fullsized by default",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Server UX",
    "website": "https://github.com/OCA/server-ux",
    "depends": ["announcement", "web_dialog_size"],
    "assets": {
        "web.assets_backend": [
            "announcement_dialog_size/static/src/js/announcement_dialog/**/*",
            "announcement_dialog_size/static/src/js/announcement_menu/**/*",
        ],
    },
}
