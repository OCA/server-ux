# Copyright 2026 CIT Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, tools
from odoo.exceptions import AccessError


class IrModelAccess(models.Model):
    _inherit = "ir.model.access"

    perm_import = fields.Boolean("Import Access", default=True)

    @api.model
    @tools.ormcache("self.env.uid", "model_name")
    def _check_import_access_cached(self, model_name):
        group_ids = self.env.user._get_group_ids()
        domain = [
            ("model_id.model", "=", model_name),
            ("perm_import", "=", True),
            "|",
            ("group_id", "=", False),
            ("group_id", "in", group_ids),
        ]
        return self.sudo().search_count(domain)

    @api.model
    def _check_import_access(self, model_name, raise_exception=True):
        """Check if the current user has permission to
        import (perm_import) for model_name."""
        if self.env.su:
            return True
        has_import = self._check_import_access_cached(model_name)
        if not has_import and raise_exception:
            raise AccessError(
                self.env._("You are not allowed to import records of model %s.")
                % model_name
            )
        return has_import
