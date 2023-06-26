# Copyright 2021 Opener B.V. <stefan@opener.amsterdam>
# Copyright 2017 Antonio Esposito <a.esposito@onestein.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models
from odoo.http import request


class Http(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        """Expose in the env whether the user is allowed to import records"""
        res = super().session_info()
        allowed_group = "base_import_security_group.group_import_csv"
        allowed_group_id = request.env.ref(allowed_group, raise_if_not_found=False)
        res["base_import_security_group__allow_import"] = (
            1 if allowed_group_id and request.env.user.has_group(allowed_group) else 0
        )
        return res
