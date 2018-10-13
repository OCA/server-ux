# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class DateRange(models.Model):

    _inherit = 'date.range'

    @api.constrains('type_id', 'date_start', 'date_end', 'company_id')
    def _validate_range(self):
        return True
