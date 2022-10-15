# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class ResGroups(models.Model):
    _inherit = "res.groups"

    def _get_exclusive_groups_data(self):
        return {
            "account.group_show_line_subtotals_tax_excluded": "Technical / Tax display B2B",
            "account.group_show_line_subtotals_tax_included": "Technical / Tax display B2C",
            "base.group_user": "User types / Access Rights",
            "base.group_portal": "User types / Portal",
            "base.group_public": "User types / Public",
        }

    @api.model
    def _get_exclusive_groups(self):
        """Return specific groups that don't have to be applied to users
        that are flagged 'Member of all Groups'
        to avoid errors (For exemple B2B / B2C that are exclusive)
        """
        return self.browse(
            [
                self.env.ref(xml_id, False).id
                for xml_id in self._get_exclusive_groups_data().keys()
                if self.env.ref(xml_id, False)
            ]
        )

    @api.model_create_multi
    def create(self, vals_list):
        ResUsers = self.env["res.users"]
        new_groups = super().create(vals_list)
        for new_group in new_groups:
            # At the creation of the groups, the group doesn't have xml_id yet
            # So we base the exclusion on the display name
            if new_group.display_name not in self._get_exclusive_groups_data().values():
                ResUsers.add_all_groups(groups=new_group)
        return new_groups
