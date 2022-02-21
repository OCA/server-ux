# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    date_format = fields.Char(
        string="Date Format",
        help="See Settings > Translations > Languages and then "
        "click on any language to see the Legends for "
        "supported Date and Time Formats and some examples",
    )
    time_format = fields.Char(
        string="Time Format",
        help="See Settings > Translations > Languages and then "
        "click on any language to see the Legends for "
        "supported Date and Time Formats and some examples",
    )
    week_start = fields.Selection(
        string="Week Start",
        selection=[
            ("1", "Monday"),
            ("2", "Tuesday"),
            ("3", "Wednesday"),
            ("4", "Thursday"),
            ("5", "Friday"),
            ("6", "Saturday"),
            ("7", "Sunday"),
        ],
    )
    decimal_point = fields.Char(
        string="Decimal Separator",
        trim=False,
        help="See Settings > Translations > Languages and then "
        "click on any language to see the Legends for "
        "supported Date and Time Formats and some examples",
    )
    thousands_sep = fields.Char(
        string="Thousands Separator",
        trim=False,
        help="See Settings > Translations > Languages and then "
        "click on any language to see the Legends for "
        "supported Date and Time Formats and some examples",
    )
