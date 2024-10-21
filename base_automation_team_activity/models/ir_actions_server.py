# Copyright 2024 Binhex - Adasat Torres
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from dateutil.relativedelta import relativedelta

from odoo import _, fields, models


class IrActionsServer(models.Model):
    _inherit = "ir.actions.server"

    activity_user_type = fields.Selection(
        selection_add=[
            ("team", _("Specific Team")),
        ],
        ondelete={"team": "cascade"},
        help="""Use 'Specific User' to always assign the same user on the next activity.
        Use 'Generic User From Record' to specify the field name of the user
        to choose on the record.
        Use 'Specific Team' to always assign the same team on the next activity.
        """,
    )
    team_id = fields.Many2one(
        comodel_name="mail.activity.team", string="Team", ondelete="cascade"
    )

    def _run_action_next_activity(self, eval_context=None):
        if (
            not self.activity_type_id
            or not self._context.get("active_id")
            or self._is_recompute()
        ):
            return False

        records = self.env[self.model_name].browse(
            self._context.get("active_ids", self._context.get("active_id"))
        )

        vals = {
            "summary": self.activity_summary or "",
            "note": self.activity_note or "",
            "activity_type_id": self.activity_type_id.id,
        }
        if self.activity_date_deadline_range > 0:
            vals["date_deadline"] = fields.Date.context_today(self) + relativedelta(
                **{
                    self.activity_date_deadline_range_type: self.activity_date_deadline_range
                }
            )
        for record in records:
            if self.activity_user_type == "team":
                vals["team_id"] = self.team_id.id
                vals["user_id"] = self.team_id.user_id.id
                record.activity_schedule(**vals)
            else:
                super()._run_action_next_activity(eval_context=eval_context)

        return False
