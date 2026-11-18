# Copyright 2026 CIT Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    def _postprocess_access_rights(self, tree):
        """Disable the import action based on the user's
        effective model access rights."""
        target_model = tree.get("model_access_rights")
        tree = super()._postprocess_access_rights(tree)

        if not target_model or tree.tag not in ("list", "kanban"):
            return tree

        if not self.env["ir.model.access"]._check_import_access(
            target_model, raise_exception=False
        ):
            tree.set("import", "0")
        return tree
