# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _add_record_id(env):
    """Add record_id field as a Reference one."""
    field_spec = [
        (
            "record_id",
            "tier.review",
            "tier_review",
            "reference",
            "varchar",
            "base_tier_validation",
        )
    ]
    openupgrade.add_fields(env, field_spec)
    query = """
        UPDATE tier_review SET record_id = model || ',' || res_id
            WHERE model IS NOT NULL AND res_id IS NOT NULL
    """
    openupgrade.logged_query(env.cr, query)


@openupgrade.migrate()
def migrate(env, version):
    _add_record_id(env)
