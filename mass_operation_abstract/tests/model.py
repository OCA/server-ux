# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class MassOperationWizardFake(models.AbstractModel):
    _inherit = "mass.operation.wizard.fake"


class MassOperationFake(models.Model):
    _name = "mass.operation.fake"
    _inherit = "mass.operation.mixin"
    _description = "Mass Editing"

    _wizard_model_name = "mass.operation.wizard.fake"
