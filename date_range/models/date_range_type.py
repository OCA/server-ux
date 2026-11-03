# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import logging
from datetime import date

from dateutil.relativedelta import relativedelta
from dateutil.rrule import DAILY, MONTHLY, WEEKLY, YEARLY

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class DateRangeType(models.Model):
    _name = "date.range.type"
    _description = "Date Range Type"
    _order = "name,id"

    @api.model
    def _default_company(self):
        return self.env.company

    name = fields.Char(required=True, translate=True)
    allow_overlap = fields.Boolean(
        help="If set, date ranges of same type must not overlap.", default=False
    )
    active = fields.Boolean(
        help="The active field allows you to hide the date range type "
        "without removing it.",
        default=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company", string="Company", index=1, default=_default_company
    )
    date_range_ids = fields.One2many("date.range", "type_id", string="Ranges")
    date_ranges_exist = fields.Boolean(compute="_compute_date_ranges_exist")

    # Defaults for generating date ranges
    name_expr = fields.Text(
        "Range name expression",
        help=(
            "Evaluated expression. E.g. "
            "\"'FY%s' % date_start.strftime('%Y%m%d')\"\nYou can "
            "use the Date types 'date_end' and 'date_start', as well as "
            "the 'index' variable."
        ),
    )
    range_name_preview = fields.Char(compute="_compute_range_name_preview", store=True)
    name_prefix = fields.Char("Range name prefix")
    duration_count = fields.Integer("Duration")
    unit_of_time = fields.Selection(
        [
            (str(YEARLY), "years"),
            (str(MONTHLY), "months"),
            (str(WEEKLY), "weeks"),
            (str(DAILY), "days"),
        ]
    )
    autogeneration_date_start = fields.Date(
        string="Autogeneration Start Date",
        help="Only applies when there are no date ranges of this type yet",
    )
    autogeneration_count = fields.Integer()
    autogeneration_unit = fields.Selection(
        [
            (str(YEARLY), "years"),
            (str(MONTHLY), "months"),
            (str(WEEKLY), "weeks"),
            (str(DAILY), "days"),
        ]
    )

    _sql_constraints = [
        (
            "date_range_type_uniq",
            "unique (name,company_id)",
            "A date range type must be unique per company !",
        )
    ]

    @api.constrains("company_id")
    def _check_company_id(self):
        if not self.env.context.get("bypass_company_validation", False):
            for rec in self.sudo():
                if not rec.company_id:
                    continue
                if bool(
                    rec.date_range_ids.filtered(
                        lambda r, drt=rec: r.company_id
                        and r.company_id != drt.company_id
                    )
                ):
                    raise ValidationError(
                        self.env._(
                            "You cannot change the company, as this "
                            "Date Range Type is assigned to Date Range '%s'."
                        )
                        % (rec.date_range_ids.display_name)
                    )

    @api.depends("name_expr", "name_prefix")
    def _compute_range_name_preview(self):
        year_start = fields.Datetime.now().replace(day=1, month=1)
        next_year = year_start + relativedelta(years=1)
        for dr_type in self:
            if dr_type.name_expr or dr_type.name_prefix:
                names = self.env["date.range.generator"]._generate_names(
                    [year_start, next_year], dr_type.name_expr, dr_type.name_prefix
                )
                dr_type.range_name_preview = names[0]
            else:
                dr_type.range_name_preview = False

    @api.depends("date_range_ids")
    def _compute_date_ranges_exist(self):
        for dr_type in self:
            dr_type.date_ranges_exist = bool(dr_type.date_range_ids)

    @api.onchange("name_expr")
    def onchange_name_expr(self):
        """Wipe the prefix if an expression is entered.

        The reverse is not implemented because we don't want to wipe the
        users' painstakingly crafted expressions by accident.
        """
        if self.name_expr and self.name_prefix:
            self.name_prefix = False

    @api.model
    def autogenerate_ranges(self):
        """Generate ranges for types with autogeneration settings"""
        logger = logging.getLogger(__name__)
        for dr_type in self.search(
            [
                ("autogeneration_count", "!=", False),
                ("autogeneration_unit", "!=", False),
                ("duration_count", "!=", False),
                ("unit_of_time", "!=", False),
            ]
        ):
            try:
                wizard = self.env["date.range.generator"].new({"type_id": dr_type.id})
                if not wizard.date_end:
                    # Nothing to generate
                    continue
                with self.env.cr.savepoint():
                    wizard.action_apply(batch=True)
            except Exception as e:
                logger.warning(
                    f"Error autogenerating ranges for date range type "
                    f"{dr_type.name}: {e}"
                )

    @api.model
    def generate_next_years_as_of_month(self):
        """Generate cumulative monthly 'As Of Month' date ranges
        for the next configured number of years."""

        date_range = self.env["date.range"]
        as_of_month_type = self.env.ref(
            "date_range.date_range_as_of_month",
            raise_if_not_found=False,
        )
        if not as_of_month_type:
            return

        Param = self.env["ir.config_parameter"].sudo()
        total_years = int(
            Param.get_param(
                "date_range.cumulative_month_range_years",
                default=5,
            )
        )

        current_year = fields.Date.today().year
        last_year = current_year + total_years

        # Prepare all candidate ranges (start_date = Jan 1,
        # end_date = last day of each month)
        candidate_ranges = []
        for year in range(current_year, last_year):
            jan_first = date(year, 1, 1)
            for month in range(1, 13):
                month_end = date(year, month, 1) + relativedelta(day=31)
                candidate_ranges.append((jan_first, month_end))

        existing_ranges = date_range.search(
            [
                ("type_id", "=", as_of_month_type.id),
                ("active", "=", True),
                ("date_start", ">=", date(current_year, 1, 1)),
                ("date_end", "<=", date(last_year - 1, 12, 31)),
            ]
        )
        existing_ranges_set = set((r.date_start, r.date_end) for r in existing_ranges)

        ranges_to_create = []
        for start_date, end_date in candidate_ranges:
            if (start_date, end_date) in existing_ranges_set:
                continue
            range_name = f"As Of {end_date:%B} {start_date:%Y} "
            ranges_to_create.append(
                {
                    "name": range_name,
                    "date_start": start_date,
                    "date_end": end_date,
                    "type_id": as_of_month_type.id,
                    "active": True,
                    "company_id": False,
                }
            )

        if ranges_to_create:
            date_range.create(ranges_to_create)
