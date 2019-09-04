# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    date_format = fields.Char(
        string='Date Format',
        help='See Settings > Translations > Languages for details',
    )
    time_format = fields.Char(
        string='Time Format',
        help='See Settings > Translations > Languages for details',
    )
    week_start = fields.Selection(
        string='Week Start',
        selection=[
            ('1', 'Monday'),
            ('2', 'Tuesday'),
            ('3', 'Wednesday'),
            ('4', 'Thursday'),
            ('5', 'Friday'),
            ('6', 'Saturday'),
            ('7', 'Sunday'),
        ],  # NOTE: Numbers as strings otherwise UI works poorly
    )
