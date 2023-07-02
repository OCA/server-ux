# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Base Field Deprecated",
    "summary": "Adds the deprecated attribute to the Odoo field model.",
    "version": "15.0.1.0.0",
    "category": "Usability",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/server-ux",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "depends": ["base"],
    "data": ["views/ir_model_fields_views.xml"],
    "maintainers": ["GuillemCForgeFlow"],
    "installable": True,
    "application": False,
    "post_init_hook": "post_init_hook",
}
