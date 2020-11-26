# Copyright 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Mass Editing",
    "version": "13.0.1.1.0",
    "author": "Serpent Consulting Services Pvt. Ltd., "
    "Tecnativa, "
    "GRAP, "
    "Odoo Community Association (OCA)",
    "category": "Tools",
    "website": "https://github.com/OCA/server-ux",
    "license": "AGPL-3",
    "summary": "Mass Editing",
    "uninstall_hook": "uninstall_hook",
    "depends": ["mass_operation_abstract"],
    "data": [
        "security/ir.model.access.csv",
        "views/mass_editing_view.xml",
        "wizard/view_mass_editing_wizard.xml",
    ],
    "demo": ["demo/mass_editing.xml"],
}
