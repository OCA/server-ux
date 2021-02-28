import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo10-addons-oca-server-ux",
    description="Meta package for oca-server-ux Odoo addons",
    version=version,
    install_requires=[
        'odoo10-addon-base_search_custom_field_filter',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
