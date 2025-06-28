{
    "name": "Server Action Wizard",
    "summary": "Run server actions with parameters via a wizard",
    "version": "18.0.1.0.0",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "maintainers": ["dreispt"],
    "website": "https://github.com/OCA/server-ux",
    "category": "Tools",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/ir_actions_server_views.xml",
        "views/server_action_wizard_views.xml",
    ],
    "installable": True,
    "application": False,
}
