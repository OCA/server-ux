# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)


from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    # By default, the permission is granted to all users (core behavior)
    env = api.Environment(cr, SUPERUSER_ID, {})
    users = env["res.users"].with_context(active_test=False).search([])
    group = env.ref("base_archive_security.group_can_archive")
    users.write({"groups_id": [(4, group.id)]})
