# Copyright 2023 Samuel RAMAROSELY
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Hide Archive Unarchive Action",
    "summary": """
        Hide Archive/Unarchive action if the user doesn't have write right""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Samuel RAMAROSELY,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-ux",
    "depends": ["web"],
    "assets": {
        "web.assets_backend": [
            "hide_archive_unarchive_action/static/src/js/form_controller.esm.js",
            "hide_archive_unarchive_action/static/src/js/list_controller.esm.js",
        ]
    },
}
