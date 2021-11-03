# Copyright (C) 2021 Ecosoft Co., Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class BaseModel(models.AbstractModel):
    _inherit = "base"

    @api.model
    def default_get(self, field_list):
        res = super().default_get(field_list)
        lines = self.env.context.get("default_line")
        field_list = self.env.context.get("default_fields")
        if lines:
            # Filter for create (0) and link (4) only
            lines = list(filter(lambda l: l[0] in (0, 1, 4), lines))
            last_line = lines[-1:][0]
            last_vals = {}
            action = last_line[0]
            # From new line
            if action == 0:
                last_vals = last_line[2]
            # From link or update
            if action in (1, 4):
                last_id = last_line[1]
                last_rec = self.browse(last_id)
                last_vals = last_rec._convert_to_write(last_rec.read()[0])
                if action == 1:
                    update_vals = last_line[2]
                    last_vals.update(update_vals)
            # if has specific field_list, filtered out unused field.
            if field_list:
                last_vals = {k: last_vals[k] for k in field_list}
            res.update(last_vals)
        return res
