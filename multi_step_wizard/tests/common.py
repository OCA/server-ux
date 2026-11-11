# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.orm.model_classes import add_to_registry

from odoo.addons.base.tests.common import BaseCommon


class CommonTestMultiStepWizard(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from .multi_step_wizard_test import MultiStepWizardTest

        add_to_registry(cls.registry, MultiStepWizardTest)
        cls.registry._setup_models__(cls.env.cr, ["multi.step.wizard.test"])
        cls.registry.init_models(
            cls.env.cr, ["multi.step.wizard.test"], {"models_to_check": True}
        )
        cls.addClassCleanup(cls.registry.__delitem__, "multi.step.wizard.test")
