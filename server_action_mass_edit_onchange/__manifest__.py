# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Server Action Mass Edit Onchange",
    "summary": """Extension of server_action_mass_edit""",
    "version": "19.0.1.0.0",
    "license": "AGPL-3",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-ux",
    "depends": ["server_action_mass_edit", "onchange_helper"],
    "data": [
        "views/ir_actions_server.xml",
    ],
}
