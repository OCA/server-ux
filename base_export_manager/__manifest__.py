# Copyright 2015 Tecnativa - Antonio Espinosa
# Copyright 2016 Tecnativa - Pedro M. Baeza
# Copyright 2018 Tecnativa - Jairo Llopis
# Copyright 2019 brain-tec AG - Olivier Jossen
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Manage model export profiles",
    "category": "Personalization",
    "version": "15.0.1.0.0",
    "depends": ["web"],
    "data": [
        "views/ir_exports.xml",
        "views/ir_model.xml",
        "views/ir_model_access.xml",
        "views/res_groups.xml",
    ],
    "qweb": ["static/src/xml/base.xml"],
    "author": "Tecnativa, "
    "LasLabs, "
    "Ursa Information Systems, "
    "brain-tec AG, "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-ux",
    "license": "AGPL-3",
    "assets": {
        "web.assets_backend": [
            "base_export_manager/static/src/js/base_export_manager.js",
        ],
        "web.assets_qweb": ["base_export_manager/static/src/xml/base.xml"],
    },
    "installable": True,
    "application": False,
}
