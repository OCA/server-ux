# Copyright 2021 ForgeFlow, S.L. (<https://wwww.forgeflow.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from openupgradelib import openupgrade  # pylint: disable=W7936

_options = [
    (True, "all"),
    (False, "none"),
]


def map_tier_definition_comment_option(env):
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("has_comment"),
        "comment_option",
        _options,
        table="tier_definition",
    )


@openupgrade.migrate()
def migrate(env, version):
    map_tier_definition_comment_option(env)
