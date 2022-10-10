{
    "name": "Base Delegation",
    "summary": "Implement a delegation process",
    "version": "14.0.1.0.0",
    "development_status": "Alpha",
    "category": "Tools",
    "website": "https://github.com/OCA/server-ux",
    "author": "Le Filament, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "security/delegation_security.xml",
        "views/delegation_view.xml",
    ],
}
