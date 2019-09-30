# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _, fields, models


class MassAction(models.Model):
    _name = "mass.action"
    _description = "Mass Actions"
    _inherit = "mass.operation.mixin"

    # Overwrite Section
    _wizard_model_name = "mass.action.wizard"

    def _prepare_action_name(self):
        return _("Mass Action (%s)" % (self.name))

    # Column Section
    python_code = fields.Text(
        string="Python Code",
        required=True,
        help="Python code that will be evaluated\n\n"
        " * self: contains the current items that can be processed\n"
        " * other python function are available like 'abs', 'min', 'any'."
        " See safe_eval() definition in odoo core to have an exhaustive list"
        " of the available functions",
        default="for item in self:\n" "    pass",
    )
