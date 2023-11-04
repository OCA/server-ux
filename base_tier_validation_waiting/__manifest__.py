# Copyright (c) 2022 brain-tec AG (https://braintec.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Base Tier Validation - Waiting status",
    "summary": "Base Tier Validation Extension to add waiting status",
    "category": "Tools",
    "version": "16.0.1.0.0",
    "author": "brain-tec AG, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-ux",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "base_tier_validation",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/tier_definition_views.xml",
    ],
    "qweb": ["static/src/xml/tier_review_template.xml"],
}
