# Copyright 2026 Ecosoft Co., Ltd. (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Base Tier Validation Correction Rules",
    "summary": "Enhance UX/UI Correct for user friendly",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "website": "https://github.com/OCA/server-ux",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "base_tier_validation_correction",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/tier_correction_wizard_views.xml",
        "views/tier_correction_rule_views.xml",
    ],
    "maintainers": ["Saran440"],
    "development_status": "Alpha",
}
