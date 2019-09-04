# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    date_format = fields.Char(
        related='company_id.date_format',
        readonly=False,
    )
    time_format = fields.Char(
        related='company_id.time_format',
        readonly=False,
    )
    week_start = fields.Selection(
        related='company_id.week_start',
        readonly=False,
    )
