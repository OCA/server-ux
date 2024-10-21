from odoo import models


class MailActivityMixin(models.AbstractModel):
    _inherit = "mail.activity.mixin"

    def activity_schedule(
        self, act_type_xmlid="", date_deadline=None, summary="", note="", **act_values
    ):
        team_id = self.env.context.get("mail_activity_team_id")
        if team_id:
            act_values.update({"team_id": team_id, "user_id": False})
        super().activity_schedule(
            act_type_xmlid, date_deadline, summary, note, **act_values
        )
