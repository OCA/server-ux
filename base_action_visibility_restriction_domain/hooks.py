# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import SUPERUSER_ID, api


def create_restrictions_window_actions(env):
    act_window_recs = env["ir.actions.act_window"].search(
        [("excluded_group_ids", "!=", False)]
    )
    aw_vals_to_create = []
    for aw in act_window_recs:
        for aw_group in aw.excluded_group_ids:
            aw_vals_to_create.append(
                {
                    "window_action_id": aw.id,
                    "group_id": aw_group.id,
                }
            )
    if aw_vals_to_create:
        env["ir.actions.restriction"].create(aw_vals_to_create)
    act_window_recs.write({"excluded_group_ids": False})


def create_restrictions_server_actions(env):
    act_server_recs = env["ir.actions.server"].search(
        [("excluded_group_ids", "!=", False)]
    )
    as_vals_to_create = []
    for serv_act in act_server_recs:
        for as_group in serv_act.excluded_group_ids:
            as_vals_to_create.append(
                {
                    "server_action_id": serv_act.id,
                    "group_id": as_group.id,
                }
            )
    if as_vals_to_create:
        env["ir.actions.restriction"].create(as_vals_to_create)
    act_server_recs.write({"excluded_group_ids": False})


def restore_groups_window_actions(env):
    restr_records = env["ir.actions.restriction"].read_group(
        [("window_action_id", "!=", False)],
        ["window_action_id", "group_id:array_agg(id)"],
        ["window_action_id"],
        lazy=False,
    )
    for restr_group in restr_records:
        env["ir.actions.act_window"].browse(restr_group["window_action_id"][0]).write(
            {"excluded_group_ids": [(6, 0, restr_group["group_id"])]}
        )


def restore_groups_server_actions(env):
    restr_records = env["ir.actions.restriction"].read_group(
        [("server_action_id", "!=", False)],
        ["server_action_id", "group_id:array_agg(id)"],
        ["server_action_id"],
        lazy=False,
    )
    for restr_group in restr_records:
        env["ir.actions.server"].browse(restr_group["server_action_id"][0]).write(
            {"excluded_group_ids": [(6, 0, restr_group["group_id"])]}
        )


def post_init_hook(cr, registry):
    """Need to migrate excluded_group_ids into ir.actions.restriction records"""
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        create_restrictions_window_actions(env)
        create_restrictions_server_actions(env)


def uninstall_hook(cr, registry):
    """Restore excluded_group_ids"""
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        restore_groups_window_actions(env)
        restore_groups_server_actions(env)
