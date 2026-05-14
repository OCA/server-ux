# Copyright 2018 Creu Blanca
# Copyright 2020 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import json

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPartnerFind(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_obj = cls.env["res.partner"]
        cls.ref = "testing_partner_internal_reference"
        cls.partner = cls.partner_obj.create(
            {"name": "Testing partner", "ref": cls.ref}
        )

    def test_partner_found_returns_form_action(self):
        action = self.partner_obj.find_res_partner_by_ref_using_barcode(self.ref)
        self.assertEqual(action["res_id"], self.partner.id)
        self.assertEqual(action["res_model"], "res.partner")
        view_id = self.env.ref("base.view_partner_form").id
        self.assertEqual(action["views"], [(view_id, "form")])

    def test_partner_not_found_returns_warning_action(self):
        unknown_ref = f"{self.ref}-{self.ref}"
        action = self.partner_obj.find_res_partner_by_ref_using_barcode(unknown_ref)
        # No partner is found, so there is no res_id on the result
        self.assertFalse(action.get("res_id", False))
        # The context must carry the warning state and message back to the wizard
        context = json.loads(action["context"])
        self.assertEqual(context.get("default_state"), "warning")
        self.assertIn(unknown_ref, context.get("default_status", ""))

    def test_barcode_action_wizard_defaults(self):
        wizard = self.env["barcode.action"].create(
            {"model": "res.partner", "method": "find_res_partner_by_ref_using_barcode"}
        )
        self.assertEqual(wizard.state, "waiting")
        self.assertEqual(wizard.status, "Start scanning")

    def test_barcode_action_rejects_private_methods(self):
        with self.assertRaises(ValidationError):
            self.env["barcode.action"].create(
                {"model": "res.partner", "method": "_compute_display_name"}
            )
