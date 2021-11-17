# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Document Quick Access Folder Auto Classification",
    "summary": """
        Auto classification of Documents after reading a QR""",
    "version": "13.0.2.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-ux",
    "depends": ["document_quick_access", "edi_storage"],
    "data": [
        "data/edi_data.xml",
        "security/security.xml",
        "wizards/document_quick_access_missing_assign.xml",
        "views/edi_exchange_record.xml",
        "data/cron_data.xml",
    ],
    "maintainers": ["etobella"],
}
