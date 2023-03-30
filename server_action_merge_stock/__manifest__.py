# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "Merge records (stock)",
    "summary": "Support merging products",
    "version": "13.0.1.0.0",
    "development_status": "Alpha",
    "category": "Extra Tools",
    "website": "https://github.com/OCA/server-ux",
    "author": "Hunki Enterprises BV, Odoo Community Association (OCA)",
    "maintainers": ["hbrunn"],
    "license": "AGPL-3",
    "depends": ["server_action_merge", "stock"],
    "demo": ["demo/ir_actions_server.xml"],
    "data": ["wizards/server_action_merge_wizard.xml"],
    "auto_install": True,
}
