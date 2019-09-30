# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    "name": "Mass Action",
    "version": "13.0.1.0.0",
    "author": "GRAP, " "Odoo Community Association (OCA)",
    "summary": "Provide the possibility to execute python code on many items"
    " from any models",
    "category": "Tools",
    "website": "https://github.com/OCA/server-ux",
    "license": "AGPL-3",
    "depends": ["mass_operation_abstract"],
    "maintainers": ["legalsylvain"],
    "data": [
        "security/ir.model.access.csv",
        "views/view_mass_action.xml",
        "views/view_mass_action_wizard.xml",
    ],
    "demo": ["demo/mass_action.xml"],
    "images": [
        "static/description/mass_action_form.png",
        "static/description/res_users_tree.png",
        "static/description/res_users_tree_result.png",
        "static/description/wizard_form_ok.png",
    ],
}
