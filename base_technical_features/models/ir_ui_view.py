# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    def _postprocess_debug(self, tree):
        # OVERRIDE to treat debug nodes as regular nodes, when technical features
        # are enabled in the user preferences.
        if self.env.user.technical_features:
            self = self.with_context(force_debug_mode=True)
        return super()._postprocess_debug(tree)
