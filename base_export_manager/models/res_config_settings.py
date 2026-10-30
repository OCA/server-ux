# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    export_denied_by_default = fields.Boolean(
        string="Deny export access by default",
        config_parameter="base_export_manager.export_denied_by_default",
    )
