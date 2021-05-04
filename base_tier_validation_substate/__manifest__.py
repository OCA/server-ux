# Copyright 2020 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Base Tier Validation Substate",
    "summary": "Change substate on tier approved",
    "version": "13.0.1.0.0",
    "development_status": "Alpha",
    "maintainers": ["kittiu"],
    "category": "Tools",
    "website": "https://github.com/OCA/server-ux",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "auto_install": True,
    "depends": ["base_tier_validation", "base_substate"],
    "data": [
        "views/tier_definition_view.xml",
    ],
}
