{
    'name': 'Base Tier Validation HR Department',
    'version': '1.0.0',
    'category': 'Human Resources',
    'summary': 'Extend Base Tier Validation with HR Department for reviewers based on users employee department',
    'author': 'SATI',
    'website': 'https://www.sati.com.py',
    'depends': ['base_tier_validation', 'hr'],
    'data': [
        'views/tier_definition_view.xml',
    ],
    'installable': True,
    'application': False,
}
