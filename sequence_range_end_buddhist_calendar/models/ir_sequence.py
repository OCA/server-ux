# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import fields, models


class IrSequence(models.Model):
    _inherit = "ir.sequence"

    use_be = fields.Boolean(
        string="Use B.E.",
        default=False,
    )

    def _get_prefix_suffix_range_end(self, date_range=None):
        context = self.env.context.copy()
        if self.use_be and context.get("ir_sequence_date_range_end"):
            context["ir_sequence_date_range_end"] += relativedelta(years=+543)
        self = self.with_context(context)
        return super()._get_prefix_suffix_range_end(date_range=date_range)
