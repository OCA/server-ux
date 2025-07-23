# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    env.cr.execute(
        """
        SELECT imf.model
        FROM ir_model_fields AS imf
        WHERE imf.name = 'review_ids'
        AND imf.ttype = 'one2many'
        AND imf.model != 'tier.validation'
        """
    )
    for (model_name,) in env.cr.fetchall():
        table_name = model_name.replace(".", "_")
        # validated column
        if not openupgrade.column_exists(env.cr, table_name, "validated"):
            openupgrade.logged_query(
                env.cr,
                f"""
                ALTER TABLE {table_name}
                ADD COLUMN IF NOT EXISTS validated BOOLEAN
                """,
            )
            # Define all those with reviews as validated and then define
            # as not validated those with unapproved reviews.
            openupgrade.logged_query(
                env.cr,
                f"""
                UPDATE {table_name} SET validated = true WHERE id IN (
                    SELECT DISTINCT(tr.res_id)
                    FROM tier_review AS tr
                    WHERE tr.model = '{model_name}'
                )
                """,
            )
            openupgrade.logged_query(
                env.cr,
                f"""
                UPDATE {table_name} SET validated = false WHERE id IN (
                    SELECT DISTINCT(tr.res_id)
                    FROM tier_review AS tr
                    WHERE tr.model = '{model_name}' AND tr.status != 'approved'
                )
                """,
            )
        # rejected column
        if not openupgrade.column_exists(env.cr, table_name, "rejected"):
            openupgrade.logged_query(
                env.cr,
                f"""
                ALTER TABLE {table_name}
                ADD COLUMN IF NOT EXISTS rejected BOOLEAN
                """,
            )
            # Define rejected if any review is rejected
            openupgrade.logged_query(
                env.cr,
                f"""
                UPDATE {table_name} SET rejected = true WHERE id IN (
                    SELECT DISTINCT(tr.res_id)
                    FROM tier_review AS tr
                    WHERE tr.model = '{model_name}' AND tr.status = 'rejected'
                )
                """,
            )
        # validation_status column
        if not openupgrade.column_exists(env.cr, table_name, "validation_status"):
            openupgrade.logged_query(
                env.cr,
                f"""
                ALTER TABLE {table_name}
                ADD COLUMN IF NOT EXISTS validation_status VARCHAR
                """,
            )
            openupgrade.logged_query(
                env.cr,
                f"""
                UPDATE {table_name} SET validation_status = 'no'
                """,
            )
            openupgrade.logged_query(
                env.cr,
                f"""
                UPDATE {table_name} SET validation_status = 'validated'
                WHERE validated = true AND coalesce(rejected, false) = false
                """,
            )
            openupgrade.logged_query(
                env.cr,
                f"""
                UPDATE {table_name} SET validation_status = 'rejected'
                WHERE validated = false AND rejected = true;
                """,
            )
            openupgrade.logged_query(
                env.cr,
                f"""
                UPDATE {table_name} SET validation_status = 'pending'
                WHERE validated = false AND coalesce(rejected, false) = false
                AND id IN (
                    SELECT DISTINCT(tr.res_id)
                    FROM tier_review AS tr
                    WHERE tr.model = '{model_name}' AND tr.status = 'pending'
                )
                """,
            )
            openupgrade.logged_query(
                env.cr,
                f"""
                UPDATE {table_name} SET validation_status = 'waiting'
                WHERE validation_status = 'no' and id IN (
                    SELECT DISTINCT(tr.res_id)
                    FROM tier_review AS tr
                    WHERE tr.model = '{model_name}' AND tr.status = 'waiting'
                )
                """,
            )
