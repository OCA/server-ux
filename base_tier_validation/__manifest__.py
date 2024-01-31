# Copyright 2017-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Base Tier Validation",
    "summary": "Implement a validation process based on tiers.",
    "version": "17.0.1.1.0",
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
            "/base_tier_validation/static/src/components/tier_review_menu/tier_review_menu.esm.js",
            "/base_tier_validation/static/src/components/tier_review_menu/tier_review_menu.xml",
            "/base_tier_validation/static/src/components/tier_review_widget/tier_review_widget.esm.js",
            "/base_tier_validation/static/src/components/tier_review_widget/tier_review_widget.scss",
            "/base_tier_validation/static/src/components/tier_review_widget/tier_review_widget.xml",
            "/base_tier_validation/static/src/js/services/tier_review_service.esm.js",
        ],
    },
}
