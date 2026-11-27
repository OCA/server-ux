# © 2016 Opener B.V. (<https://opener.am>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    @api.model
    def _visible_menu_ids(self, debug=False):
        # OVERRIDE to view menus typically shown in debug mode, when technical features
        # are enabled in the user preferences.
        if not debug and self.env.user.technical_features:
            debug = True
        return super()._visible_menu_ids(debug=debug)
