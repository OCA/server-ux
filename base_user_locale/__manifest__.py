# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'User Locale Settings',
    'version': '12.0.1.0.0',
    'author':
        'CorporateHub, '
        'Odoo Community Association (OCA)',
    'category': 'Usability',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'base_setup',
        'calendar',
        'web',
    ],
    'website': 'https://github.com/OCA/server-ux',
    'data': [
        'templates/assets.xml',
        'views/res_config_settings.xml',
        'views/res_users.xml',
    ],
    'installable': True,
}
