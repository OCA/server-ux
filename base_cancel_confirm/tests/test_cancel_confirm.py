# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from lxml import etree
from odoo_test_helper import FakeModelLoader

from odoo.tests import Form, common


class TestCancelConfirm(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestCancelConfirm, cls).setUpClass()

        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .cancel_confirm_tester import CancelConfirmTester

        cls.loader.update_registry((CancelConfirmTester,))
        cls.test_model = cls.env[CancelConfirmTester._name]
        cls.tester_model = cls.env["ir.model"].search(
            [("model", "=", "cancel.confirm.tester")]
        )

        # Access record:
        cls.env["ir.model.access"].create(
            {
                "name": "access.cancel.confirm.tester",
                "model_id": cls.tester_model.id,
                "perm_read": 1,
                "perm_write": 1,
                "perm_create": 1,
                "perm_unlink": 1,
            }
        )

        cls.test_record = cls.test_model.create({"name": "DOC-001"})

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super(TestCancelConfirm, cls).tearDownClass()

    def test_01_cancel_confirm_tester(self):
        """Cancel a document, I expect cancel_reason.
        Then, set to draft, I expect cancel_reason is deleted.
        """
        self.test_record.action_confirm()
        # Click cance, cancel confirm wizard will open. Type in cancel_reason
        res = self.test_record.action_cancel()
        ctx = res.get("context")
        self.assertEqual(ctx["cancel_method"], "action_cancel")
        self.assertEqual(ctx["default_has_cancel_reason"], "optional")
        wizard = Form(self.env["cancel.confirm"].with_context(ctx))
        wizard.cancel_reason = "Wrong information"
        wiz = wizard.save()
        # Confirm cancel on wizard
        wiz.confirm_cancel()
        self.assertEqual(self.test_record.cancel_reason, wizard.cancel_reason)
        self.assertEqual(self.test_record.state, "cancel")
        # Set to draft
        self.test_record.action_draft()
        self.assertEqual(self.test_record.cancel_reason, False)
        self.assertEqual(self.test_record.state, "draft")

    def test_view_automatic(self):
        # We need to add a view in order to test fields_view_get()
        self.env["ir.ui.view"].create(
            {
                "model": self.test_record._name,
                "name": "Demo view",
                "arch": """<form>
            <sheet>
                <group>
                    <field name="name" />
                </group>
            </sheet>
            </form>""",
            }
        )
        with Form(self.test_record) as f:
            form = etree.fromstring(f._view["arch"])
            self.assertTrue(form.xpath("//field[@name='cancel_confirm']"))
            self.assertTrue(form.xpath("//field[@name='cancel_reason']"))
