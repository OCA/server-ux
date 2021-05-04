# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime

import pytz

from odoo import _, fields, models
from odoo.exceptions import UserError


class IrSequence(models.Model):
    _inherit = "ir.sequence"

    number_of_year = fields.Integer(help="Add more number year sequence display")

    def _get_prefix_suffix_hook(self, date=None, date_range=None):
        def _interpolate(s, d):
            return (s % d) if s else ""

        def _interpolation_dict(number_of_year):
            now = range_date = effective_date = datetime.now(
                pytz.timezone(self._context.get("tz") or "UTC")
            )
            if date or self._context.get("ir_sequence_date"):
                effective_date = date or self._context.get("ir_sequence_date")
            if date_range or self._context.get("ir_sequence_date_range"):
                range_date = date_range or self._context.get("ir_sequence_date_range")

            sequences = {
                "year": "%Y",
                "month": "%m",
                "day": "%d",
                "y": "%y",
                "doy": "%j",
                "woy": "%W",
                "weekday": "%w",
                "h24": "%H",
                "h12": "%I",
                "min": "%M",
                "sec": "%S",
            }
            res = {}
            for key, format_date in sequences.items():
                res[key] = effective_date.strftime(format_date)
                res["range_" + key] = range_date.strftime(format_date)
                res["current_" + key] = now.strftime(format_date)
            if number_of_year:
                year_2_digit = str((int(res["y"]) + number_of_year) % 100)
                year = str(int(res["year"]) + number_of_year)
                res.update(
                    {
                        "y": year_2_digit,
                        "current_y": year_2_digit,
                        "range_y": year_2_digit,
                        "year": year,
                        "current_year": year,
                        "range_year": year,
                    }
                )
            return res

        d = _interpolation_dict(self.number_of_year)
        try:
            interpolated_prefix = _interpolate(self.prefix, d)
            interpolated_suffix = _interpolate(self.suffix, d)
        except ValueError:
            raise UserError(
                _("Invalid prefix or suffix for sequence '%s'") % (self.get("name"))
            )
        return interpolated_prefix, interpolated_suffix

    def _get_prefix_suffix(self, date=None, date_range=None):
        if self.number_of_year:
            return self._get_prefix_suffix_hook(date, date_range)
        return super()._get_prefix_suffix(date, date_range)
