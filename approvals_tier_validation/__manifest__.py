# Copyright 2017-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Approvals Tier Validation",
    "version": "13.0.1.0.0",
    "category": "Tools",
    "website": "https://github.com/OCA/server-ux",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["mail", "base_tier_validation_formula"],
    "data": [
        "security/tier_approval_security.xml",
        "security/ir.model.access.csv",
        "views/tier_approval_category_views.xml",
        "views/tier_approval_views.xml",
        "views/tier_definition_view.xml",
    ],
    "development_status": "alpha",
    "maintainers": ["kittiu"],
    "application": False,
    "installable": True,
}
