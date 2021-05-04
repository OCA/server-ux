# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class L10nMultiCountryDemo(models.Model):
    _name = 'l10n_multi_country.demo'
    _inherit = 'l10n_multi_country.mixin'

    name = fields.Char(
        string="Name"
    )
    custom_us_field = fields.Char(
        string="Custom us field",
        country='US'
    )


class ResCompany(models.Model):
    _name = 'res.company'
    _inherit = ['res.company', 'l10n_multi_country.mixin']

    custom_us_field = fields.Char(
        string="Custom us field",
        country='US'
    )
