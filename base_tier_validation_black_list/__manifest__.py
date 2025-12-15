# Copyright 2025 Trescloud and Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Base Tier Validation Black List",
    "summary": """
        Exception rules for tier validation used like a black list.
        The fields in the exception rules will be restricted
    """,
    "version": "18.0.1.0.1",
    "category": "Tools",
    "license": "AGPL-3",
    "development_status": "Alpha",
    "author": "Trescloud,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-ux",
    "depends": ["base_tier_validation"],
    "data": [
        "views/tier_validation_exception_views.xml",
    ],
    "demo": [],
}
