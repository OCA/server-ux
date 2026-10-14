# Copyright 2020 Akretion Mourad EL HADJ MIMOUNE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.exceptions import AccessError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import new_test_user

from .common import CommonBaseSubstate


@tagged("post_install", "-at_install", "mi_tag")
class TestBaseSubstate(CommonBaseSubstate):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Fixture operations are separate from the explicit access checks below.
        cls.env = cls.env(su=True)
        cls.sale_test_model = cls.sale_test_model.sudo()
        cls.sale_line_test_model = cls.sale_line_test_model.sudo()

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

        cls.substate_val_done = cls.env["target.state.value"].create(
            {
                "name": "Done",
                "base_substate_type_id": cls.sale_test_substate_type.id,
                "target_state_value": "done",
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

        cls.substate_to_publish = cls.base_substate.create(
            {
                "name": "To publish",
                "sequence": 5,
                "target_state_value_id": cls.substate_val_done.id,
            }
        )

        cls.substate_published = cls.base_substate.create(
            {
                "name": "Published",
                "sequence": 6,
                "target_state_value_id": cls.substate_val_done.id,
            }
        )

    def test_sale_order_substate(self):
        # Create a partner instead of using a potentially non-existent XML ID
        partner = (
            self.env["res.partner"]
            .sudo()
            .create(
                {
                    "name": "Test Partner",
                    "email": "test@example.com",
                }
            )
        )
        so_test1 = self.sale_test_model.create(
            {
                "name": "Test base substate to basic sale",
                "partner_id": partner.id,
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
        # Test that computation of sale order state change substate_id
        so_test1.line_ids.button_done()
        self.assertEqual(so_test1.state, "done")
        self.assertEqual(so_test1.substate_id, self.substate_to_publish)
        # If the state computation does not change its value,
        # it should not change the substate
        so_test1.substate_id = self.substate_published
        so_test1.line_ids.button_done()  # Triggers the recomputation despite no change
        self.assertEqual(so_test1.state, "done")
        self.assertEqual(so_test1.substate_id, self.substate_published)
        # Test that substate_id is set to false if
        # there is not substate corresponding to state
        so_test1.button_cancel()
        self.assertTrue(so_test1.state == "cancel")
        self.assertTrue(not so_test1.substate_id)

    def test_invalid_substate_state_message(self):
        sale = self.sale_test_model.create({"name": "State constraint"})
        with (
            self.assertRaisesRegex(
                ValidationError,
                "Substate To publish not defined for state New but for Done",
            ),
            self.cr.savepoint(),
        ):
            sale.substate_id = self.substate_to_publish

    def test_substate_sequence_and_archive(self):
        self.assertEqual(
            self.sale_test_model._get_default_substate_id("sale"),
            self.substate_wait_docs.id,
        )
        self.substate_wait_docs.sudo().write({"active": False})
        self.assertEqual(
            self.sale_test_model._get_default_substate_id("sale"),
            self.substate_valid_docs.id,
        )
        self.substate_in_delivering.sudo().write({"sequence": 0})
        self.assertEqual(
            self.sale_test_model._get_default_substate_id("sale"),
            self.substate_in_delivering.id,
        )

    def test_batch_computed_state_updates(self):
        sales = self.sale_test_model.create(
            [
                {
                    "name": name,
                    "line_ids": [Command.create({"name": "Line"})],
                }
                for name in ("First", "Second")
            ]
        )
        sales.line_ids.button_done()
        self.assertEqual(sales.mapped("state"), ["done", "done"])
        self.assertEqual(sales.mapped("substate_id"), self.substate_to_publish)
        sales.substate_id = self.substate_published
        sales.line_ids.button_done()
        self.assertEqual(sales.mapped("substate_id"), self.substate_published)

    def test_substate_model_consistency(self):
        sale = self.sale_test_model.create({"name": "Model constraint"})
        self.sale_test_substate_type.sudo().write(
            {"model": "base.substate.test.sale.line"}
        )
        with self.assertRaisesRegex(
            ValidationError,
            "Substate not for this object but for base.substate.test.sale.line",
        ):
            sale.check_substate_id_consistency()

    def test_substate_access_groups(self):
        user = new_test_user(
            self.env, login="substate_reader", groups="base.group_user"
        )
        manager = new_test_user(
            self.env,
            login="substate_manager",
            groups="base_substate.group_substate_manager",
        )
        for record in (
            self.sale_test_substate_type,
            self.substate_val_quotation,
            self.substate_under_negotiation,
        ):
            record.with_user(user).check_access("read")
            for operation in ("create", "write", "unlink"):
                with self.assertRaises(AccessError):
                    record.with_user(user).check_access(operation)
                record.with_user(manager).check_access(operation)
