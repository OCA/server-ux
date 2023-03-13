import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-server-ux",
    description="Meta package for oca-server-ux Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-base_optional_quick_create>=16.0dev,<16.1dev',
        'odoo-addon-base_revision>=16.0dev,<16.1dev',
        'odoo-addon-base_technical_features>=16.0dev,<16.1dev',
        'odoo-addon-base_tier_validation>=16.0dev,<16.1dev',
        'odoo-addon-base_tier_validation_formula>=16.0dev,<16.1dev',
        'odoo-addon-date_range>=16.0dev,<16.1dev',
        'odoo-addon-multi_step_wizard>=16.0dev,<16.1dev',
        'odoo-addon-server_action_mass_edit>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
