from collections import defaultdict

from odoo import api, fields, models, tools


class IrActions(models.Model):
    _inherit = "ir.actions.actions"

    priority = fields.Integer(string="Sequence", default=16, required=True)

    @api.model
    @tools.ormcache("frozenset(self.env.user.groups_id.ids)", "model_name")
    def get_bindings(self, model_name):
        """
        Order Report Actions by priority
        """
        res = super().get_bindings(model_name)
        ordered_res = defaultdict(list)
        for key, values in res.items():
            ordered_res[key] = sorted(values, key=lambda x: (x["priority"], x["id"]))
        return ordered_res
