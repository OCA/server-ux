# Copyright 2020 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Base Tier Validation Action",
    "summary": "Trigger server action after validation",
    "version": "13.0.1.0.0",
    "development_status": "Alpha",
    "maintainers": ["kittiu"],
    "category": "Tools",
    "website": "https://github.com/OCA/server-ux",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["base_tier_validation"],
    "data": ["data/job_data.xml", "views/tier_definition_view.xml"],
}
