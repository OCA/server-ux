from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        session_info = super().session_info()
        if self.env.user.has_group("base.group_user"):
            session_info["popup_announcements"] = self.env.user.popup_announcements
        return session_info
