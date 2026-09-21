# Copyright 2026 CIT Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, tools
from odoo.tools import SQL


class IrModelAccess(models.Model):
    _inherit = "ir.model.access"

    perm_archive = fields.Boolean("Archive Access", default=True)
    perm_unarchive = fields.Boolean("Unarchive Access", default=True)

    @api.model
    @tools.ormcache("self.env.uid", "mode")
    def _get_allowed_models(self, mode="read"):
        """Extend to support archive/unarchive access modes."""
        if mode not in ("archive", "unarchive"):
            return super()._get_allowed_models(mode)

        group_ids = self.env.user._get_group_ids()

        self.flush_model()
        rows = self.env.execute_query(
            SQL(
                """
            SELECT m.model
              FROM ir_model_access a
              JOIN ir_model m ON (m.id = a.model_id)
             WHERE a.perm_%s
               AND a.active
               AND (
                    a.group_id IS NULL OR
                    a.group_id IN %s
                )
            GROUP BY m.model
        """,
                SQL(mode),
                tuple(group_ids) or (None,),
            )
        )
        return frozenset(v[0] for v in rows)

    @api.model
    def get_archive_access(self, model):
        """Return archive/unarchive permission for the current user and model.
        Called by the JS layer to decide whether to show Archive/Unarchive
        action menu items.
        """
        return {
            "can_archive": self.check(model, "archive", raise_exception=False),
            "can_unarchive": self.check(model, "unarchive", raise_exception=False),
        }
