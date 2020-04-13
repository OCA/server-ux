# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class MultiStepWizardTest(models.TransientModel):
    _name = "multi.step.wizard.test"
    _description = "Multi Step Wizard Test"
    _inherit = "multi.step.wizard.mixin"
