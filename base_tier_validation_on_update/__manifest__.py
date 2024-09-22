# Copyright 2024 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Base Tier Validation On Update",
    "summary": "Validation on record modification / update",
    "version": "16.0.1.0.0",
    "category": "TODO",
    "website": "https://github.com/OCA/server-ux",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "maintainers": ["Kev-Roche"],
    "application": False,
    "installable": True,
    "depends": [
        "base_tier_validation",
    ],
    "data": [
        "views/tier_definition.xml",
        "views/tier_review.xml",
        "templates/tier_validation_templates.xml",
    ],
}
