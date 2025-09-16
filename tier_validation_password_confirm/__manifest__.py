# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
{
    "name": "Tier Validation Password Confirm",
    "version": "18.0.1.0.0",
    "category": "Server UX",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/server-ux",
    "depends": [
        "base_tier_validation",
    ],
    "data": [
        "views/tier_definition_view.xml",
        "wizards/tier_password_wizard_view.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
