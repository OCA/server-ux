import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-server-ux",
    description="Meta package for oca-server-ux Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-barcode_action',
        'odoo14-addon-base_cancel_confirm',
        'odoo14-addon-base_export_manager',
        'odoo14-addon-base_menu_visibility_restriction',
        'odoo14-addon-base_optional_quick_create',
        'odoo14-addon-base_revision',
        'odoo14-addon-base_search_custom_field_filter',
        'odoo14-addon-base_technical_features',
        'odoo14-addon-base_tier_validation',
        'odoo14-addon-base_tier_validation_formula',
        'odoo14-addon-base_tier_validation_forward',
        'odoo14-addon-base_tier_validation_server_action',
        'odoo14-addon-date_range',
        'odoo14-addon-default_multi_user',
        'odoo14-addon-document_quick_access',
        'odoo14-addon-filter_multi_user',
        'odoo14-addon-mass_editing',
        'odoo14-addon-multi_step_wizard',
        'odoo14-addon-sequence_check_digit',
        'odoo14-addon-sequence_reset_period',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
