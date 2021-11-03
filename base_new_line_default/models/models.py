# Copyright (C) 2021 Ecosoft Co., Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class BaseModel(models.AbstractModel):
    _inherit = "base"

    @api.model
    def default_get(self, field_list):
        """ Set default values based on data passed in by context """
        res = super().default_get(field_list)
        head_vals = self.env.context.get("default_src_head")
        line_vals = self.env.context.get("default_src_line")
        cols = self.env.context.get("default_dest_cols", [])
        default_vals = {}
        # default vals from one2many line
        if line_vals:
            # Filter for create (0), link (4) and write (1)
            lines = [x for x in line_vals if x[0] in (0, 1, 4)]
            last_line = lines[-1:][0]
            action = last_line[0]
            if action == 0:
                default_vals = last_line[2]
            if action in (1, 4):
                last_id = last_line[1]
                last_rec = self.browse(last_id)
                default_vals = last_rec._convert_to_write(last_rec.read(field_list)[0])
                if action == 1:
                    update_vals = last_line[2]
                    default_vals.update(update_vals)
        # default vals from direct dict
        if head_vals:
            default_vals.update(head_vals)
        # If columns are specified, set default only on those columns
        if cols:
            default_vals = {k: default_vals.pop(k) for k in cols if k in default_vals}
        res.update(default_vals)
        return res
