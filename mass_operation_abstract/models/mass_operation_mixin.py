# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _, api, fields, models


class MassOperationMixin(models.AbstractModel):
    _name = "mass.operation.mixin"
    _description = "Abstract Mass Operations"

    # To Overwrite Section (Mandatory)
    _wizard_model_name = False

    # To Overwrite Section (Optional)
    def _prepare_action_name(self):
        return _("Mass Operation (%s)" % (self.name))

    def _get_model_domain(self):
        return [("transient", "=", False)]

    # Column Section
    name = fields.Char(string="Name", required=True)

    action_name = fields.Char(string="Action Name", required=True)

    message = fields.Text(
        string="Message",
        help="If set, this message will be displayed in the" " wizard.",
    )

    model_id = fields.Many2one(
        comodel_name="ir.model",
        string="Model",
        required=True,
        ondelete="cascade",
        domain=lambda s: s._get_model_domain(),
    )

    ref_ir_act_window_id = fields.Many2one(
        comodel_name="ir.actions.act_window",
        string="Sidebar Action",
        readonly=True,
        copy=False,
    )

    group_ids = fields.Many2many(
        comodel_name="res.groups",
        relation="mass_group_rel",
        column1="mass_id",
        column2="group_id",
        string="Allowed Groups",
    )

    domain = fields.Char(string="Domain", required=True, default="[]")

    # Onchange Section
    @api.onchange("name")
    def onchange_name(self):
        if self.name and not self.action_name:
            self.action_name = self._prepare_action_name()

    # Action Section
    def enable_mass_operation(self):
        action_obj = self.env["ir.actions.act_window"]
        for mixin in self:
            if not mixin.ref_ir_act_window_id:
                mixin.ref_ir_act_window_id = action_obj.create(mixin._prepare_action())
        return True

    def disable_mass_operation(self):
        self.mapped("ref_ir_act_window_id").unlink()
        return True

    # Overload Section
    def unlink(self):
        self.disable_mass_operation()
        return super().unlink()

    def copy(self, default=None):
        default = default or {}
        default.update({"name": _("%s (copy)") % self.name})
        return super().copy(default=default)

    # Private Section
    def _prepare_action(self):
        self.ensure_one()
        return {
            "name": self.action_name,
            "type": "ir.actions.act_window",
            "res_model": self._wizard_model_name,
            "groups_id": [(6, 0, self.group_ids.ids)],
            "context": """{
                'mass_operation_mixin_id' : %d,
                'mass_operation_mixin_name' : '%s',
            }"""
            % (self.id, self._name),
            "view_mode": "form",
            "target": "new",
            "binding_model_id": self.model_id.id,
            "binding_type": "action",
        }
