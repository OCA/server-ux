# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    @api.model
    def _get_date_formats(self):
        format_date, format_time = super()._get_date_formats()
        date_format = self.env.user.date_format or self.env.company.date_format
        if date_format:
            format_date = str(date_format)
        time_format = self.env.user.time_format or self.env.company.time_format
        if time_format:
            format_time = str(time_format)
        return (format_date, format_time)
