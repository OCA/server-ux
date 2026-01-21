# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class DateRange(models.Model):
    _name = "date.range"
    _inherit = "multi.company.abstract"
    _description = "Date Range"
    _order = "type_id, date_start"
    _check_company_auto = True

    @api.model
    def _default_company(self):
        return self.env.company

    name = fields.Char(required=True, translate=True)
    date_start = fields.Date(string="Start date", required=True)
    date_end = fields.Date(string="End date", required=True)
    type_id = fields.Many2one(
        comodel_name="date.range.type",
        string="Type",
        index=True,
        required=True,
        ondelete="restrict",
        check_company=True,
    )
    company_ids = fields.Many2many(
        "res.company",
        string="Companies",
        default=_default_company,
    )
    active = fields.Boolean(
        help="The active field allows you to hide the date range without "
        "removing it.",
        compute="_compute_active",
        readonly=False,
        store=True,
    )

    @api.depends("type_id.active")
    def _compute_active(self):
        for date in self:
            if date.type_id.active:
                date.active = True
            else:
                date.active = False

    @api.constrains("type_id", "date_start", "date_end", "company_ids")
    def _validate_range(self):
        for this in self:
            if this.date_start > this.date_end:
                raise ValidationError(
                    self.env._(
                        "%(name)s is not a valid range "
                        "(%(date_start)s > %(date_end)s)"
                    )
                    % {
                        "name": this.name,
                        "date_start": this.date_start,
                        "date_end": this.date_end,
                    }
                )
            if this.type_id.allow_overlap:
                continue
            if (
                this.type_id.company_id
                and this.type_id.company_id not in this.company_ids
            ):
                raise UserError(
                    self.env._(
                        "The Date Range Type %(drt_name)s assigned to other "
                        "company, you can't change the company in "
                        "Date Range %(dt_name)s",
                        drt_name=this.type_id.name,
                        dt_name=this.name,
                    )
                )
            # here we use a plain SQL query to benefit of the daterange
            # function available in PostgresSQL
            # (http://www.postgresql.org/docs/current/static/rangetypes.html)
            SQL = """
                SELECT
                    id
                FROM
                    date_range dt
                INNER JOIN date_range_res_company_rel as rc
                ON dt.id = rc.date_range_id
                WHERE
                    DATERANGE(dt.date_start, dt.date_end, '[]') &&
                        DATERANGE(%s::date, %s::date, '[]')
                    AND dt.id != %s
                    AND dt.active
                    AND rc.res_company_id = ANY(%s)
                    AND dt.type_id=%s;"""
            self.env.cr.execute(
                SQL,
                (
                    this.date_start,
                    this.date_end,
                    this.id,
                    this.company_ids.ids,
                    this.type_id.id,
                ),
            )
            res = self.env.cr.fetchall()
            if res:
                date_ranges = self.browse(res[0])
                raise ValidationError(
                    self.env._(
                        "%(thisname)s overlaps %(dtnames)s",
                        thisname=this.name,
                        dtnames=", ".join(date_ranges.mapped("name")),
                    )
                )

    def get_domain(self, field_name):
        self.ensure_one()
        return [(field_name, ">=", self.date_start), (field_name, "<=", self.date_end)]
