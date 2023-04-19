# Copyright 2017-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Base Tier Validation",
    "summary": "Implement a validation process based on tiers.",
    "version": "15.0.1.2.1",
    "development_status": "Mature",
    "maintainers": ["LoisRForgeFlow"],
    "category": "Tools",
    "website": "https://github.com/OCA/server-ux",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["mail"],
    "data": [
        "data/mail_data.xml",
        "security/ir.model.access.csv",
        "security/tier_validation_security.xml",
        "views/res_config_settings_views.xml",
        "views/tier_definition_view.xml",
        "views/tier_review_view.xml",
        "wizard/comment_wizard_view.xml",
        "templates/tier_validation_templates.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/base_tier_validation/static/src/js/systray.js",
            "/base_tier_validation/static/src/js/tier_review_widget.js",
            "/base_tier_validation/static/src/scss/systray.scss",
            "/base_tier_validation/static/src/scss/review.scss",
        ],
        "web.assets_qweb": [
            "base_tier_validation/static/src/xml/systray.xml",
            "base_tier_validation/static/src/xml/tier_review_template.xml",
        ],
    },
}
