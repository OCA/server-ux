# Copyright 2020 Iván Todorovich (https://twitter.com/ivantodorovich)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval


class IrActionsServer(models.Model):
    _inherit = "ir.actions.server"

    domain = fields.Text(
        string="Domain",
        help="Domain verified before executing the server action. The action "
        "will only be executed on records filtered by this domain.",
        default="[]",
    )

    def run(self):
        # Overload to filter active_id and active_ids before running
        res = False
        active_model = self.env.context.get("active_model")
        active_ids = self.env.context.get("active_ids")
        active_id = self.env.context.get("active_id")
        for action in self.sudo():
            if action.domain not in (False, "[]"):
                model_name = action.model_id.model
                model = self.env[model_name]
                new_ctx = dict(self.env.context)
                new_ctx.update(
                    original_active_ids=active_ids,
                    original_active_id=active_id,
                )
                # Handle active_id
                if active_model == model_name and active_id:
                    new_active_id = list(
                        model._search(
                            expression.AND(
                                [safe_eval(action.domain), [("id", "=", active_id)]]
                            )
                        )
                    )
                    new_active_id = new_active_id and new_active_id[0] or None
                    new_ctx.update(active_id=new_active_id)
                # Handle active_ids
                if active_model == model_name and active_ids:
                    new_active_ids = list(
                        model._search(
                            expression.AND(
                                [safe_eval(action.domain), [("id", "in", active_ids)]]
                            )
                        )
                    )
                    new_ctx.update(active_ids=new_active_ids)
                # Run action with filtered context
                res = super(IrActionsServer, action.with_context(new_ctx)).run()
            else:
                res = super(IrActionsServer, action).run()
        return res
