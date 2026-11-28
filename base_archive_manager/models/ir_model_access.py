# Copyright 2026 CIT Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, tools
from odoo.exceptions import AccessError


class IrModelAccess(models.Model):
    _inherit = "ir.model.access"

    perm_archive = fields.Boolean("Archive Access", default=True)
    perm_unarchive = fields.Boolean("Unarchive Access", default=True)

    @api.model
    @tools.ormcache("self.env.uid", "model_name")
    def _check_archive_access_cached(self, model_name):
        group_ids = self.env.user._get_group_ids()
        domain = [
            ("model_id.model", "=", model_name),
            ("perm_archive", "=", True),
            "|",
            ("group_id", "=", False),
            ("group_id", "in", group_ids),
        ]
        return self.sudo().search_count(domain)

    @api.model
    def _check_archive_access(self, model_name, raise_exception=True):
        """Check if the current user has permission to archive records of model_name."""
        if self.env.su:
            return True
        has_archive = self._check_archive_access_cached(model_name)
        if not has_archive and raise_exception:
            raise AccessError(
                self.env._("You are not allowed to archive records of model %s.")
                % model_name
            )
        return has_archive

    @api.model
    @tools.ormcache("self.env.uid", "model_name")
    def _check_unarchive_access_cached(self, model_name):
        group_ids = self.env.user._get_group_ids()
        domain = [
            ("model_id.model", "=", model_name),
            ("perm_unarchive", "=", True),
            "|",
            ("group_id", "=", False),
            ("group_id", "in", group_ids),
        ]
        return self.sudo().search_count(domain)

    @api.model
    def _check_unarchive_access(self, model_name, raise_exception=True):
        """Check if the current user has permission
        to unarchive records of model_name."""
        if self.env.su:
            return True
        has_unarchive = self._check_unarchive_access_cached(model_name)
        if not has_unarchive and raise_exception:
            raise AccessError(
                self.env._("You are not allowed to unarchive records of model %s.")
                % model_name
            )
        return has_unarchive
