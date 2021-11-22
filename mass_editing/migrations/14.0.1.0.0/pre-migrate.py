# Copyright (C) 2020 - Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from psycopg2 import sql


def migrate_mass_editing(env):
    """Migrates mass.editing to ir.actions.server"""
    # Remove FK (mass_editing_id)
    openupgrade.remove_tables_fks(env.cr, ["mass_editing_line"])
    # Add legacy mass_editing_id column to server_actions
    openupgrade.logged_query(
        env.cr,
        sql.SQL(
            """
        ALTER TABLE ir_act_server
        ADD COLUMN {} int4
        """
        ).format(
            sql.Identifier(openupgrade.get_legacy_name("mass_editing_id")),
        ),
    )
    # Optional migration for server_action_domain
    # We create the domain column if it's missing, in case the module hasn't
    # been installed yet. By doing so, we make sure the domain is available
    # if the module is installed after.
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE ir_act_server
        ADD COLUMN IF NOT EXISTS domain varchar
        """,
    )
    # Create ir.actions.server for each mass.editing
    openupgrade.logged_query(
        env.cr,
        sql.SQL(
            """
        INSERT INTO ir_act_server (
            {},
            name,
            type,
            usage,
            binding_type,
            activity_user_type,
            state,
            model_id,
            model_name,
            domain
        )
        SELECT
            me.id,
            COALESCE(me.action_name, me.name),
            'ir.actions.server',
            'ir_actions_server',
            'action',
            'specific',
            'mass_edit',
            me.model_id,
            mo.model,
            me.domain
        FROM mass_editing me
        LEFT JOIN ir_model mo ON (me.model_id = mo.id)
        """
        ).format(sql.Identifier(openupgrade.get_legacy_name("mass_editing_id"))),
    )
    # Migrate mass.editing.line
    openupgrade.add_fields(
        env,
        [
            (
                "server_action_id",
                "mass.editing.line",
                "mass_editing_line",
                "integer",
                False,
                "mass_editing",
            ),
        ],
    )
    openupgrade.logged_query(
        env.cr,
        sql.SQL(
            """
        UPDATE mass_editing_line l
        SET server_action_id = sa.id
        FROM ir_act_server sa
        WHERE l.mass_editing_id = sa.{}
        """,
        ).format(sql.Identifier(openupgrade.get_legacy_name("mass_editing_id"))),
    )
    # Delete fields that no longer exist (ondelete didn't exist before)
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM mass_editing_line
        WHERE field_id IS NULL
        OR field_id NOT IN (SELECT id FROM ir_model_fields)
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.table_exists(env.cr, "mass_editing"):
        migrate_mass_editing(env)
