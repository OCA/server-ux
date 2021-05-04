# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Document Quick Access Folder Auto Classification SSh',
    'summary': """
        Auto classification of Documents after reading a QR""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Creu Blanca,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/server-ux',
    'depends': [
        'document_quick_access_folder_auto_classification',
    ],
    'data': [
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
