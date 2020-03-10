# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Document Quick Access",
    "summary": """
        Document quick access""",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-ux",
    "maintainers": ["etobella"],
    "depends": ["web", "barcode_action"],
    "data": [
        "security/ir.model.access.csv",
        "views/document_quick_access_rule.xml",
        "views/assets_backend.xml",
    ],
    "qweb": ["static/src/xml/document_quick_access_launcher.xml"],
}
