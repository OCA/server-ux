# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Admin User - All groups",
    "summary": "Automatically add admin user to all the groups",
    "version": "16.0.1.0.1",
    "category": "Tools",
    "maintainers": ["legalsylvain"],
    "author": "GRAP, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-ux",
    "installable": True,
    "depends": ["base"],
    "demo": [
        "demo/res_users.xml",
    ],
    "data": [
        "views/view_res_users.xml",
    ],
    "license": "AGPL-3",
}
