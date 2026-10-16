# Copyright 2026 CIT Services
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    def _postprocess_access_rights(self, tree):
        """Restrict the 'Archive/Unarchive' action based
        on the user's model access rights."""
        target_model = tree.get("model_access_rights")
        tree = super()._postprocess_access_rights(tree)
        if (
            not target_model
            or tree.tag not in ("list", "form", "kanban")
            or self.env.su
        ):
            return tree
        can_archive = self.env["ir.model.access"]._check_archive_access(
            target_model, raise_exception=False
        )
        can_unarchive = self.env["ir.model.access"]._check_unarchive_access(
            target_model, raise_exception=False
        )
        if not can_archive:
            tree.set("archive", "0")
        if not can_unarchive:
            tree.set("unarchive", "0")
        return tree
