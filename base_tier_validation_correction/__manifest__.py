# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Base Tier Validation Correction",
    "summary": "Correct tier.review data after it has been created.",
    "version": "14.0.1.0.0",
    "category": "Tools",
    "website": "https://github.com/OCA/server-ux",
    "author": "Ecosoft,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["base_tier_validation"],
    "data": [
        "security/correction_groups.xml",
        "security/ir.model.access.csv",
        "data/mail_data.xml",
        "data/cron_data.xml",
        "templates/tier_validation_templates.xml",
        "wizards/affected_tier_reviews.xml",
        "views/tier_correction_view.xml",
    ],
    "development_status": "Alpha",
    "maintainers": ["kittiu"],
    "application": False,
    "installable": True,
}
