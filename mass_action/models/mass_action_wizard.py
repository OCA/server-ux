# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models
from odoo.tools.safe_eval import safe_eval


class MassActionWizard(models.TransientModel):
    _name = "mass.action.wizard"
    _description = "Mass Actions Wizard"
    _inherit = "mass.operation.wizard.mixin"

    def _apply_operation(self, items):
        self.ensure_one()
        mass_action = self._get_mass_operation()
        localdict = {"self": items}
        safe_eval(mass_action.python_code, localdict, mode="exec", nocopy=True)
        return True
