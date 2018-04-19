import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-server-ux",
    description="Meta package for oca-server-ux Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-base_technical_features',
        'odoo11-addon-date_range',
        'odoo11-addon-easy_switch_user',
        'odoo11-addon-mass_editing',
        'odoo11-addon-sequence_check_digit',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
