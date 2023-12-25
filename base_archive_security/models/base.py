# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#
from odoo import _, models
from odoo.exceptions import AccessError


class Base(models.AbstractModel):
    _inherit = "base"

    def toggle_active(self):
        # check if the user is in the group that can archive/unarchive the record
        if not self.env.user.has_group("base_archive_security.group_can_archive"):
            group = self.env.ref("base_archive_security.group_can_archive")
            raise AccessError(
                _(
                    'Only users belonging to the "%s" group can archive or unarchive records.',
                    group.name,
                )
            )
        return super().toggle_active()
