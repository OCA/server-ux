# Copyright 2024 Camptocamp (<https://www.camptocamp.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)
from openupgradelib import openupgrade


def pre_init_hook(env):
    if openupgrade.table_exists(env.cr, "mass_editing_line"):
        openupgrade.rename_models(
            env.cr, [("mass.editing.line", "ir.actions.server.mass.edit.line")]
        )
        openupgrade.rename_tables(
            env.cr, [("mass_editing_line", "ir_actions_server_mass_edit_line")]
        )

        modules = [("mass_editing", "server_action_mass_edit")]
        openupgrade.update_module_names(env.cr, modules, merge_modules=True)
