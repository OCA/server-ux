# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Archive Security",
    "summary": "Controls who can archive or unarchive records",
    "version": "16.0.1.0.1",
    "website": "https://github.com/OCA/server-ux",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["imlopes", "ivantodorovich"],
    "license": "AGPL-3",
    "category": "Server tools",
    "depends": ["base"],
    "data": ["security/res_groups.xml"],
    "assets": {
        "web.assets_backend": [
            "base_archive_security/static/src/js/*.js",
        ],
    },
    "post_init_hook": "post_init_hook",
}
