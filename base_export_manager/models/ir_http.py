# Copyright 2019 brain-tec AG - Olivier Jossen
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo.http import request


class Http(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        res = super(Http, self).session_info()
        user = request.env.user
        export_models = user.fetch_export_models()
        res.update({"export_models": export_models})
        return res
