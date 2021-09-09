# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Document Quick Access Folder Auto Classification',
    'summary': """
        Auto classification of Documents after reading a QR""",
    'version': '11.0.1.0.1',
    'license': 'AGPL-3',
    'author': 'Creu Blanca,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/server-ux',
    'depends': [
        'document_quick_access',
        'queue_job',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizards/document_quick_access_missing_assign.xml',
        'views/document_quick_access_missing.xml',
        'data/config_parameter.xml',
        'data/cron_data.xml',
    ],
    'external_dependencies': {
        'python': [
            'pyzbar',
            'pdf2image',
        ],
    },
    'maintainers': [
        'etobella',
    ],
}
