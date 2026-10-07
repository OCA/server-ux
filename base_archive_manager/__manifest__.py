# Copyright 2026 CIT Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Archive Manager",
    "summary": "Manage model archive/unarchive accesses",
    "category": "Personalization",
    "version": "18.0.1.0.0",
    "depends": ["web"],
    "author": "Solomon Prabu, CIT Services, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-ux",
    "assets": {
        "web.assets_backend": [
            "base_archive_manager/static/src/js/archiveAccess.esm.js",
            "base_archive_manager/static/src/js/listController.esm.js",
            "base_archive_manager/static/src/js/formController.esm.js",
            "base_archive_manager/static/src/js/kanbanController.esm.js",
        ],
    },
    "data": ["views/ir_model_access.xml", "views/res_groups.xml"],
    "license": "AGPL-3",
    "installable": True,
}
