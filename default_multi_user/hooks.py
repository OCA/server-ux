# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json

from odoo import api, tools

from odoo.addons.base.models.ir_default import IrDefault


def post_load_hook():
    @api.model
    @tools.ormcache("self.env.uid", "model_name", "condition")
    def new_get_model_defaults(self, model_name, condition=False):
        if not hasattr(self, "_get_model_defaults_query_and_params"):
            return self.get_model_defaults_original(model_name, condition=condition)
        cr = self.env.cr
        # START OF CHANGES
        query, params = self._get_model_defaults_query_and_params(model_name, condition)
        # END OF CHANGES
        cr.execute(query, params)
        result = {}
        for row in cr.fetchall():
            # keep the highest priority default for each field
            if row[0] not in result:
                result[row[0]] = json.loads(row[1])
        return result

    if not hasattr(IrDefault, "get_model_defaults_original"):
        IrDefault.get_model_defaults_original = IrDefault.get_model_defaults

    IrDefault._patch_method("get_model_defaults", new_get_model_defaults)
