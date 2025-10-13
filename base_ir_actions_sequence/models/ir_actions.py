from odoo import fields, models, tools
from odoo.tools import frozendict


class IrActions(models.Model):
    _inherit = "ir.actions.actions"

    sequence = fields.Integer(default=16, required=True)

    @tools.ormcache("model_name", "self.env.lang")
    def _get_bindings(self, model_name):
        result = dict(super()._get_bindings(model_name))
        # Only for 'report' type, since for 'action' type the bindings are
        # managed in the original _get_bindings method
        if result.get("report"):
            result["report"] = tuple(
                sorted(result["report"], key=lambda vals: vals.get("sequence", 0))
            )
        return frozendict(result)
