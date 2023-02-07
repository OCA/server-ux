from odoo import api, fields, models, tools


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    priority = fields.Integer(string="Sequence", default=16, required=True)


class IrActions(models.Model):
    _inherit = "ir.actions.actions"

    @api.model
    @tools.ormcache("frozenset(self.env.user.groups_id.ids)", "model_name")
    def get_bindings(self, model_name):
        """
        Order Report Actions by priority
        """
        res = super().get_bindings(model_name)
        res["report"] = sorted(res["report"], key=lambda x: (x["priority"], x["id"]))
        return res
