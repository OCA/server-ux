# Copyright 2024 ooops404
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID, api


def uninstall_hook(cr, registry):
    # Restore all views
    env = api.Environment(cr, SUPERUSER_ID, {})
    customizations = env["custom.list.view"].with_context(active_test=False).search([])
    for cust in customizations:
        cust.button_roll_back()
