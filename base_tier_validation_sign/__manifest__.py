# Copyright 2023 Tecnativa - Víctor Martínez
# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Base Tier Validation Sign",
    "version": "13.0.1.0.0",
    "category": "Accounting",
    "website": "https://github.com/OCA/server-ux",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["sign_oca", "base_tier_validation"],
    "data": ["views/tier_definition_views.xml", "views/sign_request_views.xml"],
    "installable": True,
    "maintainers": ["victoralmau"],
}
