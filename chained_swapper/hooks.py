# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def uninstall_hook(env):
    """Delete the actions that were created with chained_swapper when
    the module is uninstalled"""
    env["ir.actions.act_window"].search(
        [("res_model", "=", "chained.swapper.wizard")]
    ).unlink()
    return True
