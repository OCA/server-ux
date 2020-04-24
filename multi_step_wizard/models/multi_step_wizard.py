# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class MultiStepWizard(models.AbstractModel):
    """ Mixin to ease the creation of multisteps wizards

    _selection_state must return all possible step of
    the wizard.

    For each state but final, there must be a method named
    "state_exit_X" where X is the name of the state. Each
    of these method must set the next state in self.state.

    The final state has no related method because the view
    should only display a button to close the wizard.

    open_next and _reopen_self should not need to be
    overidden, but _selection_state and state_exit_start
    likely will need to.

    """

    _name = "multi.step.wizard.mixin"
    _description = "Multi Steps Wizard Mixin"

    state = fields.Selection(
        selection="_selection_state", default="start", required=True
    )

    @api.model
    def _selection_state(self):
        return [("start", "Start"), ("final", "Final")]

    def open_next(self):
        state_method = getattr(self, "state_exit_{}".format(self.state), None)
        if state_method is None:
            raise NotImplementedError(
                "No method defined for state {}".format(self.state)
            )
        state_method()
        return self._reopen_self()

    def _reopen_self(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def state_exit_start(self):
        self.state = "final"
