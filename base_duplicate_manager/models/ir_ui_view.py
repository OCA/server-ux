# Copyright 2026 CIT Services
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    def _postprocess_access_rights(self, tree):
        """Restrict the 'Duplicate' action based on the user's model access rights."""
        target_model = tree.get("model_access_rights")
        tree = super()._postprocess_access_rights(tree)
        if not target_model or tree.tag not in ("list", "form") or self.env.su:
            return tree

        if not self.env["ir.model.access"]._check_duplicate_access(
            target_model, raise_exception=False
        ):
            tree.set("duplicate", "0")
        return tree
