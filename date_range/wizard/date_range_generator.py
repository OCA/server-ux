# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta
from dateutil.rrule import DAILY, MONTHLY, WEEKLY, YEARLY, rrule

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class DateRangeGenerator(models.TransientModel):
    _name = "date.range.generator"
    _description = "Date Range Generator"

    @api.model
    def _default_company(self):
        return self.env.company

    name_prefix = fields.Char("Range name prefix", required=True)
    date_start = fields.Date(required=True)
    type_id = fields.Many2one(
        comodel_name="date.range.type",
        string="Type",
        required=True,
        domain="['|', ('company_id', '=', company_id), " "('company_id', '=', False)]",
        ondelete="cascade",
        store=True,
        compute="_compute_type_id",
        readonly=False,
    )
    company_id = fields.Many2one(
        comodel_name="res.company", string="Company", default=_default_company
    )
    unit_of_time = fields.Selection(
        [
            (str(YEARLY), "years"),
            (str(MONTHLY), "months"),
            (str(WEEKLY), "weeks"),
            (str(DAILY), "days"),
        ],
        required=True,
    )
    duration_count = fields.Integer("Duration", required=True)
    count = fields.Integer(string="Number of ranges to generate", required=True)

    def _compute_date_ranges(self):
        self.ensure_one()
        vals = rrule(
            freq=int(self.unit_of_time),
            interval=self.duration_count,
            dtstart=self.date_start,
            count=self.count + 1,
        )
        vals = list(vals)
        date_ranges = []
        count_digits = len(str(self.count))
        for idx, dt_start in enumerate(vals[:-1]):
            date_start = dt_start.date()
            # always remove 1 day for the date_end since range limits are
            # inclusive
            date_end = vals[idx + 1].date() - relativedelta(days=1)
            date_ranges.append(
                {
                    "name": "%s%0*d" % (self.name_prefix, count_digits, idx + 1),
                    "date_start": date_start,
                    "date_end": date_end,
                    "type_id": self.type_id.id,
                    "company_id": self.company_id.id,
                }
            )
        return date_ranges

    @api.depends("company_id", "type_id.company_id")
    def _compute_type_id(self):
        if (
            self.company_id
            and self.type_id.company_id
            and self.type_id.company_id != self.company_id
        ):
            self.type_id = self.env["date.range.type"]

    @api.constrains("company_id", "type_id")
    def _check_company_id_type_id(self):
        for rec in self.sudo():
            if (
                rec.company_id
                and rec.type_id.company_id
                and rec.company_id != rec.type_id.company_id
            ):
                raise ValidationError(
                    _(
                        "The Company in the Date Range Generator and in "
                        "Date Range Type must be the same."
                    )
                )

    def action_apply(self):
        date_ranges = self._compute_date_ranges()
        if date_ranges:
            for dr in date_ranges:
                self.env["date.range"].create(dr)
        return self.env["ir.actions.act_window"].for_xml_id(
            module="date_range", xml_id="date_range_action"
        )
