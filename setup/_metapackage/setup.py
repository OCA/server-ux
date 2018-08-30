import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-server-ux",
    description="Meta package for oca-server-ux Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-barcode_action',
        'odoo11-addon-base_export_manager',
        'odoo11-addon-base_optional_quick_create',
        'odoo11-addon-base_technical_features',
        'odoo11-addon-base_tier_validation',
        'odoo11-addon-date_range',
        'odoo11-addon-easy_switch_user',
        'odoo11-addon-mass_editing',
        'odoo11-addon-sequence_check_digit',
        'odoo11-addon-sequence_reset_period',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
