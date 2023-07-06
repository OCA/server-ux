# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Web Archive Date",
    "summary": """
        Reflects the Latest Archived Date and Latest Archived by on the record metadata.
    """,
    "version": "15.0.1.0.0",
    "category": "Usability",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/server-ux",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "depends": ["web", "base_archive_date"],
    "maintainers": ["GuillemCForgeFlow"],
    "assets": {
        "web.assets_backend": [
            "web_archive_date/static/src/js/debug_manager.esm.js",
        ],
        "web.assets_qweb": ["web_archive_date/static/src/xml/debug.xml"],
    },
    "installable": True,
    "application": False,
    "auto_install": True,
}
