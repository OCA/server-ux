# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.api import SUPERUSER_ID, Environment


def migrate(cr, version):
    """Recompute the audience of group announcements.

    Since Odoo 20, ``res.groups.user_ids`` only holds the users explicitly in
    the group, so the audience is now computed from ``all_user_ids``.
    """
    if not version:
        return
    env = Environment(cr, SUPERUSER_ID, {})
    announcements = env["announcement"].with_context(active_test=False).search([])
    for fname in ("allowed_user_ids", "allowed_users_count"):
        env.add_to_compute(announcements._fields[fname], announcements)
    announcements._recompute_recordset()
