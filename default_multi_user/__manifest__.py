# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Default Multi User",
    "summary": "Allows to share user-defined defaults among several users.",
    "version": "15.0.1.0.0",
    "development_status": "Beta",
    "maintainers": ["LoisRForgeFlow"],
    "category": "Tools",
    "website": "https://github.com/OCA/server-ux",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["base"],
    "data": ["views/ir_default_view.xml"],
    "post_load": "post_load_hook",
}
