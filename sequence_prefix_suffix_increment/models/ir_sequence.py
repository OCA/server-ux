# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re

from odoo import fields, models


class IrSequence(models.Model):
    _inherit = "ir.sequence"

    prefix_increment = fields.Integer()
    suffix_increment = fields.Integer()

    def _get_prefix_suffix(self, date=None, date_range=None):
        self.ensure_one()
        prefix, suffix = super()._get_prefix_suffix(date=date, date_range=date_range)

        def increment(s, i):
            """ look for the last sequence of number(s) in a string and increment """
            numbers = re.compile(r"\d+")
            if numbers.findall(s):
                lastoccr_sre = list(numbers.finditer(s))[-1]
                lastoccr = lastoccr_sre.group()
                lastoccr_incr = str(int(lastoccr) + i)
                if len(lastoccr) > len(lastoccr_incr):
                    lastoccr_incr = lastoccr_incr.zfill(len(lastoccr))
                return (
                    s[: lastoccr_sre.start()] + lastoccr_incr + s[lastoccr_sre.end() :]
                )
            return s

        if prefix and self.prefix_increment:
            prefix = increment(prefix, self.prefix_increment)

        if suffix and self.suffix_increment:
            suffix = increment(suffix, self.suffix_increment)

        return prefix, suffix
