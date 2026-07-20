# Copyright 2026 Simone Rubino - PyTech
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade
from psycopg2.extensions import AsIs


def populate_date_order_week_day(
    env,
    module,
    model_name,
    dow_field_name,
    date_field_name,
):
    """Populate the new field `model_name.dow_field_name`.

    The computation is based on the week day of `model_name.date_field_name`.
    Use SQL to avoid Memory/Timeout errors when there are a lot of records.

    This is not used in this module but can be used in inheriting modules.
    """
    model = env[model_name]

    if not openupgrade.column_exists(env.cr, model._table, dow_field_name):
        openupgrade.add_fields(
            env,
            [
                (
                    dow_field_name,
                    model._name,
                    model._table,
                    "selection",
                    None,
                    module,
                )
            ],
        )

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE %(model_table)s so
        SET
            %(dow_field_name)s = (EXTRACT(ISODOW FROM %(date_field_name)s) - 1)::TEXT
        WHERE
            %(date_field_name)s IS NOT NULL
        """,
        {
            "model_table": AsIs(model._table),
            "dow_field_name": AsIs(dow_field_name),
            "date_field_name": AsIs(date_field_name),
        },
    )
