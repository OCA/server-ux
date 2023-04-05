# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models, tools
from odoo.exceptions import AccessError


class IrActions(models.Model):
    _inherit = "ir.actions.actions"

    @api.model
    @tools.ormcache("frozenset(self.env.user.groups_id.ids)", "model_name")
    def get_bindings(self, model_name):
        """
        Filter out actions for which user group is excluded
        """
        res = super().get_bindings(model_name)
        group_ids = set(self.env.user.groups_id.ids)
        for binding_type, actions in res.items():
            if binding_type != "action":
                continue
            actions = [
                a
                for a in actions
                if not (set(a.get("excluded_group_ids", [])) & group_ids)
            ]
            res[binding_type] = actions
        return res


class IrActionsServer(models.Model):
    _inherit = "ir.actions.server"

    excluded_group_ids = fields.Many2many(
        comodel_name="res.groups",
        relation="ir_actions_server_excluded_group_rel",
        column1="action_id",
        column2="gid",
        string="Excluded Groups",
    )

    def run(self):
        """
        Prevent action running for excluded groups
        """
        for action in self:
            action_excluded_groups = action.excluded_group_ids
            if action_excluded_groups and (
                action_excluded_groups & self.env.user.groups_id
            ):
                raise AccessError(
                    _("You don't have enough access rights to run this action.")
                )
        return super().run()


class IrActionsActWindow(models.Model):
    _inherit = "ir.actions.act_window"

    excluded_group_ids = fields.Many2many(
        comodel_name="res.groups",
        relation="ir_actions_act_window_excluded_group_rel",
        column1="action_id",
        column2="gid",
        string="Excluded Groups",
    )
