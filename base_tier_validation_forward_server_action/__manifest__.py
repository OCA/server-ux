# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Base Tier Validation - Server Action (Forward)",
    "summary": "Add option to call server action when a tier is forwarded",
    "version": "14.0.1.0.0",
    "development_status": "Alpha",
    "maintainers": ["newtratip"],
    "category": "Tools",
    "website": "https://github.com/OCA/server-ux",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["base_tier_validation_forward", "base_tier_validation_server_action"],
    "data": [
        "views/tier_definition_view.xml",
    ],
}
