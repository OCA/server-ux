# Copyright 2024 Binhex - Adasat Torres
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class IrActionsServer(models.Model):
    _inherit = "ir.actions.server"

    activity_user_type = fields.Selection(
        selection_add=[
            ("team", "Specific Team"),
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
        if self.activity_user_type == "team":
            self = self.with_context(mail_activity_team_id=self.team_id.id)
        super()._run_action_next_activity(eval_context)
        return False
