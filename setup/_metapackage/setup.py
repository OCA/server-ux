import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-server-ux",
    description="Meta package for oca-server-ux Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-barcode_action',
        'odoo12-addon-base_export_manager',
        'odoo12-addon-base_technical_features',
        'odoo12-addon-base_tier_validation',
        'odoo12-addon-base_tier_validation_formula',
        'odoo12-addon-date_range',
        'odoo12-addon-mass_editing',
        'odoo12-addon-multi_step_wizard',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
