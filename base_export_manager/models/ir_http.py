# Copyright 2019 brain-tec AG - Olivier Jossen
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo.http import request


class Http(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        """
        Odoo implementation doesn't allow add more access types, so we
        send all models where the user has the 'export' access over the
        session dictionary.
        TODO: Use other way to don't send all this data every time.
        """
        res = super().session_info()
        user = request.env.user
        export_models = user.fetch_export_models()
        res.update({"export_models": export_models})
        return res
