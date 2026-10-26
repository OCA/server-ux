# Copyright 2026 CIT Services
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class IrActionsActions(models.Model):
    _inherit = "ir.actions.actions"

    @api.model
    def get_bindings(self, model_name):
        """Filter out restricted reports from print sidebar and bindings."""
        result = super().get_bindings(model_name)
        if self.env.su:
            return result
        if "report" in result:
            report_ids = list(map(lambda rep: rep.get("id"), result["report"]))
            if reports := self.env["ir.actions.report"].browse(report_ids):
                restricted_report_ids = [
                    report.id
                    for report in reports
                    if report._is_action_report_restricted()
                ]
                if restricted_report_ids:
                    result["report"] = list(
                        filter(
                            lambda rep: rep
                            if rep.get("id") not in restricted_report_ids
                            else {},
                            result["report"],
                        )
                    )
                    if not result.get("report", False):
                        result.pop("report")
        return result
