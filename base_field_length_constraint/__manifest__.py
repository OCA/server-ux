# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Base Field Length Constraint",
    "summary": "Enforce configurable length limits on text fields, "
    "in characters or bytes",
    "version": "19.0.1.0.0",
    "category": "Tools",
    "author": "Quartile, Odoo Community Association (OCA)",
    "maintainers": ["AungKoKoLin1997"],
    "website": "https://github.com/OCA/server-ux",
    "license": "AGPL-3",
    "depends": ["bus"],
    "data": [
        "security/ir.model.access.csv",
        "security/base_field_length_rule_security.xml",
        "views/base_field_length_rule_views.xml",
    ],
    "installable": True,
}
