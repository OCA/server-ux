# Copyright 2023 Ooops404 - Ilyas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Base Action Visibility Restriction Domain",
    "version": "14.0.1.0.0",
    "category": "Extra Tools",
    "author": "Ilyas, Ooops404, Odoo Community Association (OCA)",
    "summary": "Restrict with groups and domain action access",
    "website": "https://github.com/OCA/server-ux",
    "license": "AGPL-3",
    "depends": ["base_action_visibility_restriction"],
    "maintainers": ["ilyasprogrammer"],
    "data": [
        "views/ir_actions_views.xml",
        "security/ir.model.access.csv",
    ],
    "uninstall_hook": "uninstall_hook",
    "post_init_hook": "post_init_hook",
    "installable": True,
}
