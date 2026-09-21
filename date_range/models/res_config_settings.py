from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    cumulative_month_range_years = fields.Integer(
        string="Number of Years for Cumulative Month Ranges",
        default=5,
        help=(
            "This field defines the number of years for which cumulative "
            "monthly date ranges will be automatically generated. "
            "For example, if set to 5, the system will generate cumulative "
            "monthly ranges from the current year up to the next 5 years, "
            "starting from January of each year. "
            "This is used by the 'As Of Month' date range generation method."
        ),
    )

    def set_values(self):
        res = super().set_values()
        self.ensure_one()
        self.env["ir.config_parameter"].sudo().set_param(
            "date_range.cumulative_month_range_years",
            self.cumulative_month_range_years,
        )
        return res

    @api.model
    def get_values(self):
        res = super().get_values()
        Param = self.env["ir.config_parameter"].sudo()
        res["cumulative_month_range_years"] = int(
            Param.get_param(
                "date_range.cumulative_month_range_years",
                default=5,
            )
        )
        return res
