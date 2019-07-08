# Copyright 2017-19 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Base Tier Validation",
    "summary": "Implement a validation process based on tiers.",
    "version": "12.0.3.1.0",
    "development_status": "Mature",
    "maintainers": ['lreficent'],
    "category": "Tools",
    "website": "https://github.com/OCA/server-ux",
    "author": "Eficent, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "web",
        "bus",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/tier_definition_view.xml",
        "views/tier_review_view.xml",
        "views/assets_backend.xml",
    ],
    'qweb': [
        'static/src/xml/systray.xml',
        'static/src/xml/tier_review_template.xml',
    ],
}
