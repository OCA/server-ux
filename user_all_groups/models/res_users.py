# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    has_all_groups = fields.Boolean(string="Member of all Groups")

    @api.model_create_multi
    def create(self, vals_list):
        new_users = super().create(vals_list)
        self.add_all_groups(users=new_users)
        return new_users

    def write(self, vals):
        res = super().write(vals)
        self.add_all_groups(users=self)
        return res

    @api.model
    def add_all_groups(self, users=False, groups=False):
        """Add all groups to users, except 'exclusive groups'.

        if users is defined, users list will be filtered with only the ones
        flagged 'Member of all groups'.
        if users is undefined, apply to all the users flagged as 'Member of all groups'
        """
        if self.env.context.get("add_all_groups_disabled"):
            return

        ResGroups = self.env["res.groups"]
        if not users:
            users = self.with_context(active_test=False).search([])
        users = users.filtered(lambda x: x.has_all_groups)

        if not groups:
            groups = ResGroups.search([])
        groups -= ResGroups._get_exclusive_groups()

        if not groups or not users:
            return

        _logger.info(
            "Automatically add %(user_qty)d user(s) (%(user_names)s)"
            " to %(group_qty)d group(s) (%(group_names)s)"
            % (
                {
                    "user_qty": len(users),
                    "user_names": ",".join(users.mapped("name")),
                    "group_qty": len(groups),
                    "group_names": ",".join(groups.mapped("display_name")),
                }
            )
        )
        users.with_context(add_all_groups_disabled=True).write(
            {
                "groups_id": [(4, group_id) for group_id in groups.ids],
            }
        )
