# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class ResBranch(models.Model):
    _name = "res.branch"
    _description = "Company Branches"

    name = fields.Char(string="Branch", required=True)
    company_id = fields.Many2one(
        comodel_name="res.company", required=True, string="Company"
    )
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one(
        comodel_name="res.country.state",
        string="Fed. State",
        domain="[('country_id', '=?', country_id)]",
    )
    country_id = fields.Many2one(comodel_name="res.country")
    email = fields.Char()
    phone = fields.Char()
    active = fields.Boolean(default=True)

    _sql_constraints = [("name_uniq", "unique(name)", "Branch must be unique!")]
