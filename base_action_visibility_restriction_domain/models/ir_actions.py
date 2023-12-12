# Copyright 2023 Ooops404 - Ilyas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models, tools
from odoo.exceptions import AccessError
from odoo.tools.safe_eval import safe_eval


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
            filtered_actions = []
            for act in actions:
                act_rec = self.env[act["type"]].browse(act["id"])
                restrictions = act_rec.restriction_ids.filtered(
                    lambda x: x.group_id.id in group_ids
                )
                if restrictions and any(restrictions.mapped("condition_domain")):
                    # if at least one has domain then action is visible
                    # and execution access will be defined in run()
                    # otherwise action is hidden.
                    filtered_actions.append(act)
                elif restrictions and not any(restrictions.mapped("condition_domain")):
                    # all restrictions are without domain. Action inaccessible.
                    continue
                else:
                    # no restriction. Action accessible.
                    filtered_actions.append(act)
            res[binding_type] = filtered_actions
        return res


class IrActionsServer(models.Model):
    _inherit = "ir.actions.server"

    restriction_ids = fields.One2many("ir.actions.restriction", "server_action_id")

    def run(self):
        """
        Prevent action running based on groups and domain
        """
        group_ids = self.env.user.groups_id.ids
        for action in self.sudo():
            restrictions = action.restriction_ids.filtered(
                lambda x: x.group_id.id in group_ids
            )
            rec_ids = self.env.context.get("active_id") or self.env.context.get(
                "active_ids"
            )
            records = self.env[self.model_name].browse(rec_ids)
            for restr in restrictions:
                if restr.condition_domain in ["[]", False, ""]:
                    # no domain: block
                    raise AccessError(
                        _("You don't have enough access rights to run this action.")
                    )
                # domain allows to run action
                filtered_records = records.filtered_domain(
                    safe_eval(restr.condition_domain)
                )
                blocked_records = records - filtered_records
                if blocked_records:
                    raise AccessError(
                        _(
                            "You don't have enough access rights to run "
                            "this action on records: %s." % blocked_records
                        )
                    )
        return super().run()


class IrActionsActWindow(models.Model):
    _inherit = "ir.actions.act_window"

    restriction_ids = fields.One2many("ir.actions.restriction", "window_action_id")

    def read(self, fields=None, load="_classic_read"):
        if (
            not self.env.context.get("active_ids")
            and not self.env.context.get("active_id")
        ) or not self.binding_model_id:
            return super(IrActionsActWindow, self).read(fields=fields, load=load)
        restrictions = self.restriction_ids.filtered(
            lambda x: x.group_id.id in self.env.user.groups_id.ids
        )
        deny = False
        rec_ids = self.env.context.get("active_id") or self.env.context.get(
            "active_ids"
        )
        records = self.env[self.binding_model_id.model].browse(rec_ids)
        blocked_records = False
        for restr in restrictions:
            if restr.condition_domain not in ["[]", False, ""]:
                # domain allows to run action
                filtered_records = records.filtered_domain(
                    safe_eval(restr.condition_domain)
                )
                blocked_records = records - filtered_records
                if not blocked_records:
                    # all records available for action
                    continue
                else:
                    # some records are blocked - raise error
                    deny = True
                    break
            else:
                # one restriction without domain - block access right away
                deny = True
                break
        if deny:
            if blocked_records:
                raise AccessError(
                    _(
                        "You don't have enough access rights to "
                        "run this action on records: %s." % blocked_records
                    )
                )
            else:
                raise AccessError(
                    _("You don't have enough access rights to run this action.")
                )
        else:
            return super(IrActionsActWindow, self).read(fields=fields, load=load)


class IrActionRestriction(models.Model):
    _name = "ir.actions.restriction"
    _description = "Actions Restriction"

    server_action_id = fields.Many2one("ir.actions.server")
    window_action_id = fields.Many2one("ir.actions.act_window")
    group_id = fields.Many2one("res.groups")
    condition_domain = fields.Char(help="Defines records on which group can run action")
    model = fields.Char(compute="_compute_model")

    @api.depends("server_action_id", "window_action_id")
    def _compute_model(self):
        for rec in self:
            if rec.server_action_id:
                rec.model = rec.server_action_id.model_name
            else:
                rec.model = rec.window_action_id.binding_model_id.model
