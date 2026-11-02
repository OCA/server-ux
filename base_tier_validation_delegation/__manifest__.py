# Copyright 2026 360ERP (<https://www.360erp.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Base Tier Validation Delegation",
    "summary": "Allows users to delegate tier validation tasks when out of office.",
    "version": "18.0.1.0.0",
    "development_status": "Beta",
    "category": "Tools",
    "website": "https://github.com/OCA/server-ux",
    "author": "360 ERP, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["base_tier_validation"],
    "data": [
        "security/delegation_security.xml",
        "data/cron.xml",
        "views/res_users_views.xml",
        "views/tier_review_views.xml",
    ],
}
