# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    date_format = fields.Char(
        help="See Settings > Translations > Languages and then "
        "click on any language to see the Legends for "
        "supported Date and Time Formats and some examples",
    )
    time_format = fields.Char(
        help="See Settings > Translations > Languages and then "
        "click on any language to see the Legends for "
        "supported Date and Time Formats and some examples",
    )
    week_start = fields.Selection(
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

    @property
    def SELF_READABLE_FIELDS(self):
        base_user_locale_readable_fields = [
            "date_format",
            "time_format",
            "week_start",
            "decimal_point",
            "thousands_sep",
        ]
        return super().SELF_READABLE_FIELDS + base_user_locale_readable_fields

    def preference_save(self):
        super().preference_save()
        # Do a "full" reload instead of just a context_reload to apply locale
        # user specific settings.
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }
