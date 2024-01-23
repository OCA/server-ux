{
    "name": "Base Field Access Right",
    "author": "ForgeFlow,Odoo Community Association (OCA)",
    "summary": "Configure access right permissions at field level",
    "version": "15.0.1.0.1",
    "license": "LGPL-3",
    "maintainer": ["jordibforgeflow"],
    "website": "https://github.com/OCA/server-ux",
    "category": "web",
    "depends": [
        "base",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/field_access_right_views.xml",
    ],
    "installable": True,
}
