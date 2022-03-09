# Copyright 2022 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

from odoo import models


class ResUsers(models.Model):
    _inherit = "res.users"

    def _can_import_remote_urls(self):
        """By default only superadmin is able to do so that makes not much sense"""
        res = super()._can_import_remote_urls()
        if not res:
            # if not admin
            import_image_grp = self.env.ref(
                "base_import_image_url_user.group_import_image_from_url"
            )
            if import_image_grp in self.env.user.groups_id:
                return True
        return res
