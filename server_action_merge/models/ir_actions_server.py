# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import fields, models


class IrActionsServer(models.Model):
    _inherit = "ir.actions.server"

    state = fields.Selection(selection_add=[("merge", "Merge records")])
    merge_method = fields.Selection(
        [("orm", "ORM"), ("sql", "SQL")], default="orm", string="Merge method"
    )
    merge_handling = fields.Selection(
        [("delete", "Delete"), ("deactivate", "Deactivate"), ("none", "Do nothing")],
        string="Merged records handling",
        default="delete",
        help="This determines what to do with records that have been merged into "
        "another one, default is to delete them",
    )
    merge_sudo = fields.Boolean("Run merge as superuser", default=False)

    def run_action_merge_multi(self, action, eval_context=None):
        """Return the merge wizard"""
        wizard = self.env["server.action.merge.wizard"].create({"action_id": action.id})
        wizard._onchange_line_ids()
        return {
            "type": "ir.actions.act_window",
            "name": action.name,
            "res_model": wizard._name,
            "res_id": wizard.id,
            "target": "new",
            "view_mode": "form",
            "context": self.env.context,
        }
