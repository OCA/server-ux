# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Base Tier Validation - Allow Disable Restart",
    "summary": "Allow disabling restart validation",
    "version": "16.0.1.0.0",
    "development_status": "Beta",
    "maintainers": ["maisim"],
    "category": "Tools",
    "website": "https://github.com/OCA/server-ux",
    "author": "OpenStudio SAS, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["base_tier_validation", "base_tier_validation_waiting"],
    "data": [
        "templates/tier_validation_templates.xml",
        "views/tier_definition_views.xml",
    ],
}
