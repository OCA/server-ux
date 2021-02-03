# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Base Tier Validation Forward",
    "summary": "Forward option for base tiers",
    "version": "14.0.1.0.2",
    "category": "Tools",
    "website": "https://github.com/OCA/server-ux",
    "author": "Ecosoft,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["base_tier_validation"],
    "data": [
        "security/ir.model.access.csv",
        "data/mail_data.xml",
        "views/tier_definition_view.xml",
        "wizard/forward_wizard_view.xml",
        "templates/tier_validation_templates.xml",
    ],
    "development_status": "Alpha",
    "maintainers": ["kittiu"],
    "application": False,
    "installable": True,
    "qweb": ["static/src/xml/tier_review_template.xml"],
    "uninstall_hook": "uninstall_hook",
}
