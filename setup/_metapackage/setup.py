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
        'odoo12-addon-base_import_security_group',
        'odoo12-addon-base_optional_quick_create',
        'odoo12-addon-base_search_custom_field_filter',
        'odoo12-addon-base_substate',
        'odoo12-addon-base_technical_features',
        'odoo12-addon-base_tier_validation',
        'odoo12-addon-base_tier_validation_formula',
        'odoo12-addon-base_user_locale',
        'odoo12-addon-chained_swapper',
        'odoo12-addon-date_range',
        'odoo12-addon-default_multi_user',
        'odoo12-addon-document_quick_access',
        'odoo12-addon-document_quick_access_folder_auto_classification',
        'odoo12-addon-filter_multi_user',
        'odoo12-addon-mass_editing',
        'odoo12-addon-mass_operation_abstract',
        'odoo12-addon-multi_step_wizard',
        'odoo12-addon-sequence_check_digit',
        'odoo12-addon-sequence_reset_period',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
