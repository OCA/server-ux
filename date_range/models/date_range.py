# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class DateRange(models.Model):
    _name = "date.range"
    _description = "Date Range"
    _order = "type_name,date_start"

    @api.model
    def _default_company(self):
        return self.env.company

    name = fields.Char(required=True, translate=True)
    date_start = fields.Date(string="Start date", required=True)
    date_end = fields.Date(string="End date", required=True)
    type_id = fields.Many2one(
        comodel_name="date.range.type",
        string="Type",
        index=1,
        required=True,
        ondelete="restrict",
        domain="['|', ('company_id', '=', company_id), " "('company_id', '=', False)]",
        store=True,
        compute="_compute_type_id",
        readonly=False,
    )
    type_name = fields.Char(related="type_id.name", store=True, string="Type Name")
    company_id = fields.Many2one(
        comodel_name="res.company", string="Company", index=1, default=_default_company
    )
    active = fields.Boolean(
        help="The active field allows you to hide the date range without "
        "removing it.",
        default=True,
    )

    _sql_constraints = [
        (
            "date_range_uniq",
            "unique (name,type_id, company_id)",
            "A date range must be unique per company !",
        )
    ]

    @api.depends("company_id", "type_id.company_id")
    def _compute_type_id(self):
        """Enforce check of company consistency when changing company, here
        or in the type.
        """
        self._check_company_id_type_id()

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
                        "The Company in the Date Range and in "
                        "Date Range Type must be the same."
                    )
                )

    @api.constrains("type_id", "date_start", "date_end", "company_id")
    def _validate_range(self):
        for this in self:
            if this.date_start > this.date_end:
                raise ValidationError(
                    _("%(r1)s is not a valid range (%(r2)s > %(r3)s)")
                    % {"r1": this.name, "r2": this.date_start, "r3": this.date_end}
                )
            if this.type_id.allow_overlap:
                continue
            # here we use a plain SQL query to benefit of the daterange
            # function available in PostgresSQL
            # (http://www.postgresql.org/docs/current/static/rangetypes.html)
            SQL = """
                SELECT
                    id
                FROM
                    date_range dt
                WHERE
                    DATERANGE(dt.date_start, dt.date_end, '[]') &&
                        DATERANGE(%s::date, %s::date, '[]')
                    AND dt.id != %s
                    AND dt.active
                    AND dt.company_id = %s
                    AND dt.type_id=%s;"""
            self.env.cr.execute(
                SQL,
                (
                    this.date_start,
                    this.date_end,
                    this.id,
                    this.company_id.id or None,
                    this.type_id.id,
                ),
            )
            res = self.env.cr.fetchall()
            if res:
                dt = self.browse(res[0][0])
                raise ValidationError(
                    _("%(rr)s overlaps %(rt)s") % {"rr": this.name, "rt": dt.name}
                )

    def get_domain(self, field_name):
        self.ensure_one()
        return [(field_name, ">=", self.date_start), (field_name, "<=", self.date_end)]
