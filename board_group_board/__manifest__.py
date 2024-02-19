# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "Group-specific dashboards",
    "summary": "Allow defining dashboards per group and impose them on users",
    "version": "15.0.1.0.0",
    "development_status": "Alpha",
    "category": "Productivity",
    "website": "https://github.com/OCA/server-ux",
    "author": "Hunki Enterprises BV, Verdigado eG, Odoo Community Association (OCA)",
    "maintainers": ["hbrunn"],
    "license": "AGPL-3",
    "depends": [
        "board",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/board_group_board.xml",
    ],
    "demo": [
        "demo/board_group_board.xml",
    ],
}
