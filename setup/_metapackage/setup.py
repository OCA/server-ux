import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-server-ux",
    description="Meta package for oca-server-ux Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-barcode_action>=15.0dev,<15.1dev',
        'odoo-addon-base_menu_visibility_restriction>=15.0dev,<15.1dev',
        'odoo-addon-base_substate>=15.0dev,<15.1dev',
        'odoo-addon-base_technical_features>=15.0dev,<15.1dev',
        'odoo-addon-base_tier_validation>=15.0dev,<15.1dev',
        'odoo-addon-chained_swapper>=15.0dev,<15.1dev',
        'odoo-addon-date_range>=15.0dev,<15.1dev',
        'odoo-addon-default_multi_user>=15.0dev,<15.1dev',
        'odoo-addon-document_quick_access>=15.0dev,<15.1dev',
        'odoo-addon-filter_multi_user>=15.0dev,<15.1dev',
        'odoo-addon-mass_editing>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
