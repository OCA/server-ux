# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Res Groups Access Request",
    "summary": "Users can reuqest access to groups",
    "version": "15.0.1.0.0",
    "development_status": "Alpha",
    "maintainers": ["AaronHForgeFlow"],
    "category": "Tools",
    "website": "https://github.com/OCA/server-ux",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_groups_access_request_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "res_groups_access_request/static/src/js/access_request_widget.js"
        ],
        "web.assets_qweb": [
            "res_groups_access_request/static/src/xml/access_request_widget.xml"
        ],
    },
}
