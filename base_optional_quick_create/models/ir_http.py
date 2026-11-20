from odoo import models


class Http(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        session_info = super().session_info()
        models_no_quick_create = (
            self.env["ir.model"]
            .sudo()
            .search([("avoid_quick_create", "=", True)])
            .mapped("model")
        )
        session_info["avoid_quick_create_models"] = models_no_quick_create
        return session_info
