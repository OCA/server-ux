# Copyright 2026 CIT Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    def _get_import_group_ids(self):
        """Helper to get user group IDs for import check.
        Overridden by role integration."""
        return self.env.user.groups_id.ids

    def _postprocess_access_rights(self, tree):
        """Disable the import action based on the user's
        effective model access rights."""
        target_model = tree.get("model_access_rights")
        tree = super()._postprocess_access_rights(tree)

        if not target_model or tree.tag not in ("list", "kanban"):
            return tree

        group_ids = self._get_import_group_ids()
        has_import = bool(
            self.env["ir.model.access"]
            .sudo()
            .search(
                [
                    ("model_id.model", "=", target_model),
                    ("perm_import", "=", True),
                    "|",
                    ("group_id", "=", False),
                    ("group_id", "in", group_ids),
                ],
                limit=1,
            )
        )

        if not has_import:
            tree.set("import", "0")

        return tree
