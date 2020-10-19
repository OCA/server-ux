# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    old_pattern = r"$$'mass_editing_object' : ([0-9]*)$$"
    new_pattern = (
        r"$$'mass_operation_mixin_id' : \1, "
        r"'mass_operation_mixin_name' : 'mass.editing', $$"
    )
    openupgrade.logged_query(
        env.cr,
        r"""UPDATE ir_act_window
        SET context = regexp_replace(context, %(old_pattern)s, %(new_pattern)s)
        WHERE context ~ %(old_pattern)s
        """ % {
            'old_pattern': old_pattern,
            'new_pattern': new_pattern,
        }
    )
