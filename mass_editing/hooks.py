# Copyright 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.api import SUPERUSER_ID, Environment


def uninstall_hook(cr, registry):
    """Delete the actions that were created with mass_editing when
    the module is uninstalled"""
    env = Environment(cr, SUPERUSER_ID, {})
    env["ir.actions.act_window"].search(
        [("res_model", "=", "mass.editing.wizard")]
    ).unlink()
    return True
