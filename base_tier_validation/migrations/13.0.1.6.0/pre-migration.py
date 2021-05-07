# Copyright 2021 ForgeFlow, S.L. (<https://wwww.forgeflow.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from openupgradelib import openupgrade

_column_renames = {
    "tier_definition": [("has_comment", None)],
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, _column_renames)
