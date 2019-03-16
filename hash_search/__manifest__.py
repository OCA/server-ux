# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Hash Search',
    'summary': "Allows to search any kind of record through a QR scanner",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Creu Blanca, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/server-ux',
    'depends': [
        'barcode_action',
        'printer_zpl2',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/assets_backend.xml',
        'wizards/barcode_action.xml',
    ],
    'qweb': [
        'static/src/xml/hash_search_launcher.xml'
    ]
}
