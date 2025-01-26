from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class TestConfirmationWizard(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )

    def test_confirm_message(self):
        """Test flow when create confirmation wizard with method"""
        confirmation_wizard_obj = self.env["confirmation.wizard"]

        # Default behavior
        action = confirmation_wizard_obj.confirm_message(
            "Message Test",
            self.partner,
        )
        excepted_action = self.env["ir.actions.actions"]._for_xml_id(
            "confirmation_wizard.confirmation_wizard_action"
        )
        excepted_action["context"] = self.env.context

        # Wizard with title and context
        excepted_title = "Confirm Wizard"
        action = confirmation_wizard_obj.with_context(hide_cancel=True).confirm_message(
            "Message Test", self.partner, title=excepted_title
        )
        self.assertEqual(action["name"], excepted_title, "Title must be the same")
        self.assertTrue(
            action["context"]["hide_cancel"], "Invisible Cancel must be True"
        )

    def test_confirm_no_action_message(self):
        """Test flow when create confirmation wizard with window close"""
        confirmation_wizard_obj = self.env["confirmation.wizard"]

        excepted_title = "Confirm Wizard"
        action = confirmation_wizard_obj.confirm_message(
            "Message Test", self.partner, title=excepted_title
        )
        self.assertEqual(action["name"], excepted_title, "Title must be the same")

    def test_action_confirm_method(self):
        """Test flow when confirm wizard with return type method"""
        vals = {
            "message": "Message Test",
            "res_ids": "",
            "return_type": "method",
            "res_model": "res.partner",
            "callback_method": "",
            "callback_params": {},
        }
        wizard = self.env["confirmation.wizard"].create(vals)
        with self.assertRaises(UserError) as e:
            wizard.action_confirm()
        self.assertEqual(
            str(e.exception), "Records (IDS: '') not found in model 'res.partner'."
        )

        vals1 = {**vals, "res_ids": ",".join(map(str, self.partner.ids))}
        wizard = self.env["confirmation.wizard"].create(vals1)
        with self.assertRaises(UserError) as e:
            wizard.action_confirm()
        self.assertEqual(
            str(e.exception), "Method '' is not found on model 'res.partner'."
        )

        vals2 = {
            **vals1,
            "callback_method": "write",
            "callback_params": {"vals": {"name": "New Partner #1"}},
        }
        wizard = self.env["confirmation.wizard"].create(vals2)
        result = wizard.action_confirm()
        self.assertTrue(result, "Result must be True")
        self.assertEqual(
            self.partner.name,
            "New Partner #1",
            "Partner name must be equal to 'New Partner #1'",
        )

    def test_action_confirm_window_close(self):
        """Test flow when confirm wizard with return type window close"""
        wizard = self.env["confirmation.wizard"].create(
            {
                "message": "Message Confirmation Text",
                "return_type": "window_close",
            }
        )
        result = wizard.action_confirm()
        self.assertDictEqual(
            result, {"type": "ir.actions.act_window_close"}, "Dicts must be the same"
        )
