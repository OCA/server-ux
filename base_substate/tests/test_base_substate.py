# Copyright 2020 Akretion Mourad EL HADJ MIMOUNE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.tests import tagged

from .common import CommonBaseSubstate


@tagged("post_install", "-at_install", "mi_tag")
class TestBaseSubstate(CommonBaseSubstate):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.substate_type = cls.env["base.substate.type"]
        cls.base_substate = cls.env["base.substate"]

        cls.mail_template = cls.env["mail.template"].create(
            {
                "name": "Waiting for legal documents",
                "model_id": cls.env["ir.model"]._get(cls.sale_test_model._name).id,
                "subject": "Test Email Substate",
            }
        )
        cls.sale_test_substate_type = cls.substate_type.create(
            {
                "name": "Sale",
                "model": "base.substate.test.sale",
                "target_state_field": "state",
            }
        )

        cls.substate_val_quotation = cls.env["target.state.value"].create(
            {
                "name": "Quotation",
                "base_substate_type_id": cls.sale_test_substate_type.id,
                "target_state_value": "draft",
            }
        )

        cls.substate_val_sale = cls.env["target.state.value"].create(
            {
                "name": "Sale order",
                "base_substate_type_id": cls.sale_test_substate_type.id,
                "target_state_value": "sale",
            }
        )
        cls.substate_under_negotiation = cls.base_substate.create(
            {
                "name": "Under negotiation",
                "sequence": 1,
                "target_state_value_id": cls.substate_val_quotation.id,
            }
        )

        cls.substate_won = cls.base_substate.create(
            {
                "name": "Won",
                "sequence": 1,
                "target_state_value_id": cls.substate_val_quotation.id,
            }
        )

        cls.substate_wait_docs = cls.base_substate.create(
            {
                "name": "Waiting for legal documents",
                "sequence": 2,
                "target_state_value_id": cls.substate_val_sale.id,
                "mail_template_id": cls.mail_template.id,
            }
        )

        cls.substate_valid_docs = cls.base_substate.create(
            {
                "name": "To validate legal documents",
                "sequence": 3,
                "target_state_value_id": cls.substate_val_sale.id,
            }
        )

        cls.substate_in_delivering = cls.base_substate.create(
            {
                "name": "In delivering",
                "sequence": 4,
                "target_state_value_id": cls.substate_val_sale.id,
            }
        )
        cls.test_partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "email": "test@test.com",
            }
        )

    def test_sale_order_substate(self):
        so_test1 = self.sale_test_model.create(
            {
                "name": "Test base substate to basic sale",
                "partner_id": self.test_partner.id,
                "line_ids": [
                    Command.create({"name": "line test", "amount": 120.0, "qty": 1.5})
                ],
            }
        )
        self.assertTrue(so_test1.state == "draft")
        self.assertTrue(so_test1.substate_id == self.substate_under_negotiation)
        self.assertNotIn(
            self.mail_template.subject, so_test1.message_ids.mapped("subject")
        )
        # Test that validation of sale order change substate_id
        so_test1.button_confirm()
        self.assertTrue(so_test1.state == "sale")
        self.assertTrue(so_test1.substate_id == self.substate_wait_docs)
        # Check some message_ids are created and sent email
        self.assertIn(
            self.mail_template.subject, so_test1.message_ids.mapped("subject")
        )
        # Test that substate_id is set to false if
        # there is not substate corresponding to state
        so_test1.button_cancel()
        self.assertTrue(so_test1.state == "cancel")
        self.assertTrue(not so_test1.substate_id)

    def test_constrain_substate_mismatch(self):
        """Test function when substate does not belong to current state."""
        so_test2 = self.sale_test_model.create(
            {
                "name": "Test base substate to basic sale",
                "partner_id": self.test_partner.id,
                "line_ids": [
                    Command.create({"name": "line test 2", "amount": 120.0, "qty": 1.5})
                ],
            }
        )
        self.assertTrue(so_test2.state == "draft")
        self.assertTrue(so_test2.substate_id == self.substate_under_negotiation)

        so_test2.write({"state": "sale"})
        so_test2.write({"substate_id": self.substate_wait_docs.id})
        self.assertTrue(so_test2.substate_id == self.substate_wait_docs)

    def test_write_triggers_default_substate(self):
        """state field automatically sets the default substate."""
        so = self.sale_test_model.create(
            {
                "name": "Test Auto Substate on Write",
                "partner_id": self.test_partner.id,
                "line_ids": [
                    Command.create({"name": "line test 3", "amount": 230.0, "qty": 3})
                ],
            }
        )
        self.assertTrue(so.state == "draft")
        self.assertTrue(so.substate_id == self.substate_under_negotiation)

        so.write({"state": "sale"})

        self.assertTrue(so.state == "sale")
        self.assertTrue(so.substate_id == self.substate_wait_docs)

    def test_create_with_explicit_substate(self):
        """Create with explicit substate."""
        so = self.sale_test_model.create(
            {
                "name": "Test Explicit Substate",
                "partner_id": self.test_partner.id,
                "line_ids": [
                    Command.create({"name": "line test 4", "amount": 230.0, "qty": 2})
                ],
                "substate_id": self.substate_won.id,
            }
        )
        self.assertTrue(so.state == "draft")
        self.assertTrue(so.substate_id == self.substate_won)
        self.assertNotIn(self.mail_template.subject, so.message_ids.mapped("subject"))
