# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval


class MassOperationWizardMixin(models.AbstractModel):
    _name = "mass.operation.wizard.mixin"
    _description = "Abstract Mass Operations Wizard"

    _OPERATION_STATUS_SELECTION = [
        ("info", "Info"),
        ("warning", "Warning"),
        ("danger", "Danger"),
    ]

    # To Overwrite Section
    def _apply_operation(self, items):
        self.ensure_one()
        pass

    # Column Section
    selected_item_qty = fields.Integer(readonly=True)

    remaining_item_qty = fields.Integer(readonly=True)

    operation_description_info = fields.Text(readonly=True)
    operation_description_warning = fields.Text(readonly=True)
    operation_description_danger = fields.Text(readonly=True)

    message = fields.Text(readonly=True)

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)

        mass_operation = self._get_mass_operation()

        operation_description_info = False
        operation_description_warning = False
        operation_description_danger = False

        # Compute items quantity
        active_ids = self.env.context.get("active_ids")
        remaining_items = self._get_remaining_items()

        if len(active_ids) == len(remaining_items):
            operation_description_info = _(
                "The treatment will be processed on the %d selected"
                " elements." % (len(active_ids))
            )
        elif len(remaining_items):
            operation_description_warning = _(
                "You have selected %d items that can not be processed."
                " Only %d items will be processed."
                % (len(active_ids) - len(remaining_items), len(remaining_items))
            )
        else:
            operation_description_danger = _(
                "None of the %d items you have selected can be processed."
                % (len(active_ids))
            )

        res.update(
            {
                "selected_item_qty": len(active_ids),
                "remaining_item_qty": len(remaining_items),
                "operation_description_info": operation_description_info,
                "operation_description_warning": operation_description_warning,
                "operation_description_danger": operation_description_danger,
                "message": mass_operation.message,
            }
        )
        return res

    def button_apply(self):
        items = self._get_remaining_items()
        if not len(items):
            raise UserError(
                _(
                    "there is no more element that corresponds to the rules of"
                    " the domain.\n Please refresh your list and try to"
                    " select again the items."
                )
            )
        return self._apply_operation(items)

    # Private Section
    @api.model
    def _get_mass_operation(self):
        IrModel = self.env["ir.model"]
        mass_operation_models = IrModel.search(
            [("model", "=", self.env.context.get("mass_operation_mixin_name", False))]
        )
        if len(mass_operation_models) != 1:
            return False
        MassOperationModel = self.env[mass_operation_models[0].model]
        return MassOperationModel.search(
            [("id", "=", self.env.context.get("mass_operation_mixin_id", 0))]
        )

    @api.model
    def _get_remaining_items(self):
        active_ids = self.env.context.get("active_ids", [])
        mass_operation = self._get_mass_operation()
        SrcModel = self.env[mass_operation.model_id.model]
        if mass_operation.domain != "[]":
            domain = expression.AND(
                [safe_eval(mass_operation.domain), [("id", "in", active_ids)]]
            )
        else:
            domain = [("id", "in", active_ids)]
        return SrcModel.search(domain)
