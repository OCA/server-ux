from odoo_test_helper import FakeModelLoader

from odoo.tests import SavepointCase


class TestMassOperationMixin(SavepointCase, FakeModelLoader):
    @classmethod
    def setUpClass(cls):
        super(TestMassOperationMixin, cls).setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .models import MassOperationFake, MassOperationWizardFake

        cls.loader.update_registry(
            (
                MassOperationWizardFake,
                MassOperationFake,
            )
        )

        cls.lang = cls.env.ref("base.lang_en")
        cls.MassOperationFake = cls.env["mass.operation.fake"]

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super(TestMassOperationMixin, cls).tearDownClass()

    def test_create_auto_url(self):
        self.asserTrue(True)
