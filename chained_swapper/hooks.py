# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.api import SUPERUSER_ID, Environment


def uninstall_hook(cr, registry):
    """Delete the actions that were created with chained_swapper when
    the module is uninstalled"""
    env = Environment(cr, SUPERUSER_ID, {})
    env["ir.actions.act_window"].search(
        [("res_model", "=", "chained.swapper.wizard")]
    ).unlink()
    return True
