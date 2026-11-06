# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Base Tier Validation Review History",
    "summary": "Keep completed tier reviews as history instead of deleting them",
    "version": "16.0.1.0.0",
    "category": "Tools",
    "website": "https://github.com/OCA/server-ux",
    "author": "Quartile, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["base_tier_validation"],
    "data": [
        "views/res_config_settings_views.xml",
        "views/tier_definition_view.xml",
        "views/tier_review_view.xml",
        "templates/tier_validation_templates.xml",
    ],
    "development_status": "Alpha",
    "maintainers": ["smorita7749"],
    "installable": True,
}
