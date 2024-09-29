# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import datetime

import pytz

from odoo import _, fields, models
from odoo.exceptions import UserError


class IrSequence(models.Model):
    _inherit = "ir.sequence"

    def _get_prefix_suffix(self, date=None, date_range=None):
        if "range_end_" in str(self.prefix) or "range_end_" in str(self.suffix):
            return self._get_prefix_suffix_range_end(date_range=date_range)
        else:
            return super()._get_prefix_suffix(date=date, date_range=date_range)

    def _get_prefix_suffix_range_end(self, date=None, date_range=None):
        def _interpolate(s, d):
            return (s % d) if s else ""

        def _interpolation_dict():
            now = range_date = range_end_date = effective_date = datetime.now(
                pytz.timezone(self._context.get("tz") or "UTC")
            )
            if date or self._context.get("ir_sequence_date"):
                effective_date = fields.Datetime.from_string(
                    date or self._context.get("ir_sequence_date")
                )
            if date_range or self._context.get("ir_sequence_date_range"):
                range_date = fields.Datetime.from_string(
                    date_range or self._context.get("ir_sequence_date_range")
                )
            if date_range or self._context.get("ir_sequence_date_range_end"):
                range_end_date = fields.Datetime.from_string(
                    date_range or self._context.get("ir_sequence_date_range_end")
                )

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
            for key, sequence_format in sequences.items():
                res[key] = effective_date.strftime(sequence_format)
                res["current_" + key] = now.strftime(sequence_format)
                res["range_" + key] = range_date.strftime(sequence_format)
                res["range_end_" + key] = range_end_date.strftime(sequence_format)
            return res

        self.ensure_one()
        d = _interpolation_dict()
        try:
            interpolated_prefix = _interpolate(self.prefix, d)
            interpolated_suffix = _interpolate(self.suffix, d)
        except ValueError:
            raise UserError(
                _("Invalid prefix or suffix for sequence '%s'") % self.name
            ) from None
        return interpolated_prefix, interpolated_suffix


class IrSequenceDateRange(models.Model):
    _inherit = "ir.sequence.date_range"

    def _next(self):
        self = self.with_context(ir_sequence_date_range_end=self.date_to)
        return super()._next()
