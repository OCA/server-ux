# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.orm.model_classes import add_to_registry
from odoo.tests import common


class CommonTestMultiStepWizard(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        from .multi_step_wizard_test import MultiStepWizardTest

        add_to_registry(cls.registry, MultiStepWizardTest)
        cls.registry._setup_models__(cls.env.cr, ["multi.step.wizard.test"])
        cls.registry.init_models(
            cls.env.cr, ["multi.step.wizard.test"], {"models_to_check": True}
        )
        cls.addClassCleanup(cls.registry.__delitem__, "multi.step.wizard.test")
