# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, new_test_user

LOGGER = "odoo.addons.base_field_length_constraint.models.base_field_length_rule"


class TestBaseFieldLengthRule(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.rule_model = cls.env["base.field.length.rule"]
        fields_model = cls.env["ir.model.fields"]
        cls.partner_model = cls.env["ir.model"]._get("res.partner")
        cls.ref_field = fields_model._get("res.partner", "ref")
        cls.comment_field = fields_model._get("res.partner", "comment")
        cls.company = cls.env["res.company"].create({"name": "Company A"})
        cls.other_company = cls.env["res.company"].create({"name": "Company B"})
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.user = new_test_user(
            cls.env,
            login="bflc_user",
            groups="base.group_user,base.group_partner_manager",
        )

    def _create_rule(self, **values):
        return self.rule_model.create(
            {
                "name": "Test Rule",
                "model_id": self.partner_model.id,
                "field_id": self.ref_field.id,
                "max_length": 5,
                **values,
            }
        )

    def test_char_measure(self):
        self._create_rule()
        self.partner.ref = "東京都港区"
        with self.assertRaises(ValidationError):
            self.partner.ref = "123456"
        with self.assertRaises(ValidationError):
            self.env["res.partner"].create({"name": "New", "ref": "123456"})

    def test_byte_measure(self):
        self._create_rule(measure="byte", encoding="cp932")
        self.partner.ref = "12345"
        with self.assertRaises(ValidationError):
            self.partner.ref = "あいう"

    def test_html_measure(self):
        self._create_rule(field_id=self.comment_field.id)
        self.partner.comment = "<p><strong>Hi</strong></p>"
        with self.assertRaises(ValidationError):
            self.partner.comment = "<p>Hello World</p>"

    def test_error_message(self):
        rule = self._create_rule(name="WMS IF-01")
        with self.assertRaisesRegex(ValidationError, "WMS IF-01"):
            self.partner.ref = "123456"
        rule.message = "Too long for the WMS."
        with self.assertRaisesRegex(ValidationError, "Too long for the WMS."):
            self.partner.ref = "123456"

    def test_condition_domain(self):
        self._create_rule(condition_domain="[('is_company', '=', True)]")
        self.partner.ref = "123456"
        with self.assertRaises(ValidationError):
            self.partner.is_company = True
        # The scope is read after company_type has been inversed.
        partner = (
            self.env["res.partner"]
            .with_context(default_is_company=True)
            .create({"name": "Person", "ref": "123456", "company_type": "person"})
        )
        self.assertFalse(partner.is_company)
        with self.assertRaises(ValidationError):
            self.env["res.partner"].create(
                {"name": "Company", "ref": "123456", "company_type": "company"}
            )

    def test_company_scope(self):
        branch = self.env["res.company"].create(
            {"name": "Branch", "parent_id": self.company.id}
        )
        self._create_rule(company_id=self.company.id)
        self.partner.company_id = self.other_company
        self.partner.ref = "123456"
        with self.assertRaises(ValidationError):
            self.partner.company_id = branch

    def test_warning_enforcement(self):
        self._create_rule(enforcement="warning")
        with (
            self.assertLogs(LOGGER, level="WARNING"),
            patch.object(self.env.registry["res.users"], "_bus_send") as bus_send,
        ):
            self.partner.ref = "123456"
        self.assertEqual(self.partner.ref, "123456")
        self.assertIn("Test Rule", bus_send.call_args[0][1]["message"])

    def test_onchange_warning(self):
        rule = self._create_rule(enforcement="warning")
        field = self.env["res.partner"]._fields["ref"]
        self.assertTrue(self.env["res.partner"]._has_onchange(field, []))
        result = self.env["res.partner"].onchange(
            {"name": "Test Partner", "ref": "123456"}, ["ref"], {"ref": {}}
        )
        self.assertEqual(result["warning"]["type"], "dialog")
        self.assertIn("Test Rule", result["warning"]["message"])
        rule.enforcement = "error"
        result = self.env["res.partner"].onchange(
            {"name": "Test Partner", "ref": "123456"}, ["ref"], {"ref": {}}
        )
        self.assertNotIn("warning", result)

    def test_rule_changes_apply_immediately(self):
        rule = self._create_rule()
        with self.assertRaises(ValidationError):
            self.partner.ref = "123456"
        rule.max_length = 10
        self.partner.ref = "123456"
        rule.active = False
        self.partner.ref = "12345678901"

    def test_unusable_condition_is_skipped(self):
        rule = self._create_rule(condition_domain="[('is_company', '=', True)]")
        self.env.cr.execute(
            "UPDATE base_field_length_rule SET condition_domain = %s WHERE id = %s",
            ["[('x_gone', '=', True)]", rule.id],
        )
        rule.invalidate_recordset()
        self.env.registry.clear_cache()
        with self.assertLogs(LOGGER, level="WARNING"):
            self.partner.ref = "123456"

    def test_validate_records(self):
        self.partner.ref = "123456"
        self._create_rule()
        violations = self.rule_model.validate_records(
            self.partner, raise_on_error=False
        )
        self.assertEqual(violations[0]["length"], 6)
        with self.assertRaises(ValidationError):
            self.rule_model.validate_records(self.partner)

    def test_check_value(self):
        self._create_rule(measure="byte", encoding="cp932")
        self.assertFalse(self.rule_model.check_value("res.partner", "ref", "12345"))
        with self.assertRaises(ValidationError):
            self.rule_model.check_value("res.partner", "ref", "あいう")
        self._create_rule(
            name="Company rule",
            max_length=1,
            condition_domain="[('is_company', '=', True)]",
        )
        self.assertFalse(
            self.rule_model.check_value("res.partner", "ref", "12", record=self.partner)
        )
        self.partner.is_company = True
        with self.assertRaisesRegex(ValidationError, "Company rule"):
            self.rule_model.check_value("res.partner", "ref", "12", record=self.partner)

    def test_action_check_existing_records(self):
        partner = self.env["res.partner"].create({"name": "Long", "ref": "123456"})
        archived = self.env["res.partner"].create(
            {"name": "Archived", "ref": "123456", "active": False}
        )
        rule = self._create_rule()
        action = rule.action_check_existing_records()
        found = (
            self.env["res.partner"]
            .with_context(**action["context"])
            .search(action["domain"])
        )
        self.assertLessEqual(partner + archived, found)
        rule.condition_domain = "[('name', '=', 'No Such Partner')]"
        action = rule.action_check_existing_records()
        self.assertEqual(action["params"]["type"], "success")

    def test_non_admin(self):
        # The rule and the condition are read as sudo for any user.
        self.partner.country_id = self.env.ref("base.jp")
        self.env["ir.rule"].create(
            {
                "name": "No country",
                "model_id": self.env["ir.model"]._get("res.country").id,
                "domain_force": "[(0, '=', 1)]",
                "groups": [Command.link(self.env.ref("base.group_user").id)],
            }
        )
        self._create_rule(condition_domain="[('country_id.code', '=', 'JP')]")
        self.env.invalidate_all()
        # Mail tracking would read the country too, as the user.
        partner = self.partner.with_user(self.user).with_context(tracking_disable=True)
        with self.assertRaisesRegex(ValidationError, "Test Rule"):
            partner.ref = "123456"

    def test_invalid_rule_is_refused(self):
        fields_model = self.env["ir.model.fields"]
        cases = {
            "field of another model": (
                {"field_id": fields_model._get("res.country", "address_format").id},
                "does not belong to model",
            ),
            "unstored field": (
                {"field_id": fields_model._get("res.partner", "contact_address").id},
                "is not stored",
            ),
            "unmeasurable field": (
                {"field_id": fields_model._get("res.partner", "tz").id},
                "Only char, text, html",
            ),
            "unknown encoding": (
                {"measure": "byte", "encoding": "not-an-encoding"},
                "Unknown encoding",
            ),
            "invalid condition": (
                {"condition_domain": "[('no_such_field', '=', True)]"},
                "Invalid condition",
            ),
        }
        for label, (values, expected) in cases.items():
            with (
                self.subTest(label),
                self.assertRaisesRegex(ValidationError, expected),
                self.cr.savepoint(),
            ):
                self._create_rule(**values)
