# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def migrate(cr, installed_version):
    if not installed_version or openupgrade.table_exists(cr, 'mass_editing'):
        return

    openupgrade.rename_tables(cr, [('mass_object', 'mass_editing')])
    if not openupgrade.column_exists(cr, 'mass_editing', 'action_name'):
        copy_vals = {'mass_editing': [('name', 'action_name', None)]}
        openupgrade.copy_columns(cr, copy_vals)
