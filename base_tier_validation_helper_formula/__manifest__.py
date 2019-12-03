# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Base Tier Validation Helper Formula',
    'version': '12.0.1.0.0',
    'category': 'Tools',
    'author': 'Ecosoft, '
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'https://github.com/OCA/server-ux',
    'depends': [
        'base_tier_validation_formula',
        'base_tier_validation_helper',
        'hr',
    ],
    'data': [
        'views/tier_definition_helper_view.xml',
    ],
    'maintainer': [
        'ps-tubtim',
    ],
    'installable': True,
    'development_status': 'Alpha',
}
