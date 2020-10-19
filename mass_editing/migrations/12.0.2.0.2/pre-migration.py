# Copyright 2020 Vauxoo - Luis González
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if not openupgrade.column_exists(env.cr, 'mass_editing', 'action_name'):
        openupgrade.copy_columns(
            env.cr, {'mass_editing': [('name', 'action_name', None)]}
        )
