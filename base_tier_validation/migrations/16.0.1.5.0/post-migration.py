# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)

from openupgradelib import openupgrade  # pylint: disable=W7936


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.m2o_to_x2m(
        env.cr,
        env["tier.definition"],
        "tier_definition",
        "reviewer_ids",
        openupgrade.get_legacy_name("reviewer_id"),
    )
