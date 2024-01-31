# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)

from openupgradelib import openupgrade  # pylint: disable=W7936


@openupgrade.migrate()
def migrate(env, version):
    if not openupgrade.column_exists(env.cr, "tier_definition", "reviewer_ids"):
        openupgrade.rename_columns(env.cr, {"tier_definition": [("reviewer_id", None)]})
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE tier_definition
        SET review_type = 'individuals'
        WHERE review_type = 'individual'
        """,
    )
