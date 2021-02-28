# -*- coding: utf-8 -*-
# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Add custom filters for fields via UI",
    "version": "10.0.1.0.1",
    "category": "Usability",
    "website": "https://github.com/OCA/server-ux",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "demo": [
        "demo/demo_ir_ui_custom_field_filter.xml",
    ],
    "data": [
        "security/ir.model.access.csv",
        "templates/assets.xml",
        "views/ir_ui_custom_field_filter_views.xml",
    ],
    "depends": ["web"],
    "license": "AGPL-3",
    "installable": True,
    "maintainers": ["pedrobaeza"],
}
