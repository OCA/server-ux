# Copyright 2022 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Base Tier Validation Bypass",
    "summary": "All authorized user to set bypass tier on any document",
    "version": "14.0.1.0.0",
    "category": "Tools",
    "website": "https://github.com/OCA/server-ux",
    "author": "Ecosoft,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["base_tier_validation_forward"],
    "data": [
        "security/security.xml",
        "data/mail_data.xml",
        "wizard/forward_wizard_view.xml",
        "templates/tier_validation_templates.xml",
    ],
    "development_status": "Alpha",
    "maintainers": ["kittiu"],
    "application": False,
    "installable": True,
    "qweb": ["static/src/xml/tier_review_template.xml"],
}
