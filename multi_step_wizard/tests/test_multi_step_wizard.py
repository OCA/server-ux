# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import tagged

from .common import CommonTestMultiStepWizard


@tagged("post_install", "-at_install")
class TestMultiStepWizard(CommonTestMultiStepWizard):
    def setUp(self):
        super().setUp()
        self.MultiStepWizard = self.env["multi.step.wizard.test"]

    def test_behavior(self):
        wizard = self.MultiStepWizard.create({})
        wizard.open_next()
        self.assertEqual(wizard.state, "final")
        with self.assertRaises(NotImplementedError):
            wizard.open_next()
        self.assertTrue(wizard.allow_back)
        wizard.open_previous()
        self.assertEqual(wizard.state, "start")
