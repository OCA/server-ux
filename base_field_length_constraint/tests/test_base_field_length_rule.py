# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from psycopg2 import IntegrityError

from odoo import Command
from odoo.exceptions import AccessError, ValidationError
from odoo.tests.common import TransactionCase, new_test_user
from odoo.tools import mute_logger

from odoo.addons.base_field_length_constraint.models import (
    base_field_length_rule as rule_module,
)
from odoo.addons.web.models import models as web_models

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
        cls.country_model = cls.env["ir.model"]._get("res.country")
        cls.country_format_field = fields_model._get("res.country", "address_format")
        cls.company = cls.env["res.company"].create(
            {"name": "Field Length Rule Company"}
        )
        cls.other_company = cls.env["res.company"].create(
            {"name": "Field Length Rule Other Company"}
        )
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

    def _violating_partner(self, **values):
        """A partner breaching a 5-character rule on ``ref``, created before it.

        This is the data that predates a rule.
        """
        return self.env["res.partner"].create(
            {"name": "Long Ref Partner", "ref": "123456", **values}
        )

    def _onchange_ref(self, value, field_names=("ref",), user=None):
        model = self.env["res.partner"]
        if user:
            model = model.with_user(user)
        return model.onchange(
            {"name": "Test Partner", "ref": value}, list(field_names), {"ref": {}}
        )

    def _cool_down(self, model_name="res.partner"):
        """Warm the ormcache and drop the ORM cache, as a real request finds them.

        Creating a rule leaves it prefetched, which masks a missing sudo on the
        read path.
        """
        self.rule_model._get_rules(model_name)
        self.env.invalidate_all()

    # Measurement

    def test_char_measure(self):
        self._create_rule()
        self.partner.ref = "12345"  # the boundary passes
        self.partner.ref = "東京都港区"  # 5 characters, 15 UTF-8 bytes
        with self.assertRaises(ValidationError):
            self.partner.ref = "123456"

    def test_byte_measure(self):
        rule = self._create_rule(measure="byte", encoding="cp932")
        self.partner.ref = "12345"  # five half-width characters, five bytes
        with self.assertRaises(ValidationError):
            self.partner.ref = "あいう"  # three characters, six cp932 bytes
        # An unmappable character is replaced, not raised on.
        rule.encoding = "ascii"
        self.partner.ref = "あいうえお"  # five characters, five replacement bytes
        with self.assertRaises(ValidationError):
            self.partner.ref = "あいうえおか"
        with self.assertRaises(ValidationError):
            self.rule_model._measure_length("x", "byte", "not-an-encoding")

    def test_html_measure(self):
        self._create_rule(field_id=self.comment_field.id)
        self.partner.comment = "<p><strong>Hi</strong></p>"  # 26 of markup, 2 of text
        # What the editor stores for an empty field renders to nothing.
        spec = self.rule_model._get_rules("res.partner")[0]
        self.assertFalse(self.rule_model._get_measurable_value("<p><br></p>", spec))
        with self.assertRaises(ValidationError):
            self.partner.comment = "<p>Hello World</p>"

    # Write paths

    def test_error_on_create(self):
        self._create_rule()
        with self.assertRaises(ValidationError):
            self.env["res.partner"].create({"name": "New Partner", "ref": "123456"})

    def test_stored_computed_field(self):
        field = self.env["ir.model.fields"]._get(
            "res.partner", "commercial_company_name"
        )
        self._create_rule(field_id=field.id)
        with self.assertRaises(ValidationError):
            self.env["res.partner"].create(
                {"name": "A Very Long Company Name", "is_company": True}
            )

    def test_unwritten_field_is_not_rechecked(self):
        partner = self._violating_partner(is_company=True)
        self._create_rule()
        self._create_rule(
            name="Conditional", condition_domain="[('is_company', '=', True)]"
        )
        partner.name = "Renamed Partner"
        self.assertEqual(partner.ref, "123456")

    def test_excluded_names_are_skipped(self):
        partner = self._violating_partner()
        self._create_rule()
        partner._validate_fields({"ref"}, {"ref"})
        with self.assertRaises(ValidationError):
            partner._validate_fields({"ref"})

    # Messages

    def test_error_message(self):
        self._create_rule(name="WMS interface IF-01")
        with self.assertRaises(ValidationError) as error:
            self.partner.ref = "123456"
        self.assertIn("WMS interface IF-01", str(error.exception))
        self.assertIn("Test Partner", str(error.exception))
        self.rule_model.search([]).message = "The reference is too long for the WMS."
        with self.assertRaises(ValidationError) as error:
            self.partner.ref = "1234567"
        self.assertIn("too long for the WMS", str(error.exception))

    def test_every_violated_rule_is_reported(self):
        self._create_rule(name="Loose rule", max_length=10)
        self._create_rule(name="Tight rule", max_length=5)
        with self.assertRaises(ValidationError) as error:
            self.partner.ref = "1234567"
        self.assertIn("Tight rule", str(error.exception))
        self.assertNotIn("Loose rule", str(error.exception))
        with self.assertRaises(ValidationError) as error:
            self.partner.ref = "12345678901"
        self.assertIn("Loose rule", str(error.exception))

    def test_error_and_warning_on_the_same_write(self):
        self._create_rule(name="Blocking rule")
        self._create_rule(name="Warning rule", enforcement="warning", max_length=3)
        with self.assertNoLogs(LOGGER, level="WARNING"):
            with self.assertRaises(ValidationError) as error:
                self.partner.ref = "123456"
        self.assertIn("Blocking rule", str(error.exception))
        self.assertNotIn("Warning rule", str(error.exception))

    # Scoping

    def test_condition_domain(self):
        self._create_rule(condition_domain="[('is_company', '=', True)]")
        # Not a company, so out of scope.
        self.partner.ref = "123456"
        self.env["res.partner"].create({"name": "Person Partner", "ref": "123456"})
        company_partner = self.env["res.partner"].create(
            {"name": "Company Partner", "is_company": True}
        )
        with self.assertRaises(ValidationError):
            company_partner.ref = "123456"
        with self.assertRaises(ValidationError):
            self.env["res.partner"].create(
                {"name": "Company Partner", "is_company": True, "ref": "123456"}
            )

    def test_condition_field_brings_the_record_into_scope(self):
        self._create_rule(condition_domain="[('is_company', '=', True)]")
        for label, values in (
            ("condition field", {"is_company": True}),
            ("field inversing into it", {"company_type": "company"}),
        ):
            with self.subTest(label):
                partner = self.env["res.partner"].create(
                    {"name": "Person Partner", "ref": "123456"}
                )
                with self.assertRaises(ValidationError):
                    partner.write(values)

    def test_scope_is_read_after_the_inverses(self):
        # The ORM validates the stored fields before the inverse of
        # company_type has run, when the record still holds the default the
        # contact menu gave it.
        self._create_rule(condition_domain="[('is_company', '=', True)]")
        partner = (
            self.env["res.partner"]
            .with_context(default_is_company=True)
            .create(
                {"name": "Person Partner", "ref": "123456", "company_type": "person"}
            )
        )
        self.assertFalse(partner.is_company)
        company_partner = self.env["res.partner"].create(
            {"name": "Company Partner", "is_company": True}
        )
        company_partner.write({"company_type": "person", "ref": "123456"})
        self.assertEqual(company_partner.ref, "123456")
        # The marker create() sets must not outlive it.
        with self.assertRaises(ValidationError):
            partner.is_company = True

    def test_company_scope(self):
        self._create_rule(company_id=self.company.id)
        self.partner.company_id = self.other_company
        self.partner.ref = "123456"  # the rule belongs to another company
        self.partner.ref = False
        self.partner.company_id = self.company
        with self.assertRaises(ValidationError):
            self.partner.ref = "123456"
        moved = self._violating_partner(company_id=self.other_company.id)
        with self.assertRaises(ValidationError):
            moved.company_id = self.company

    def test_company_scope_covers_branches(self):
        branch = self.env["res.company"].create(
            {"name": "Field Length Rule Branch", "parent_id": self.company.id}
        )
        self._create_rule(company_id=self.company.id)
        self.partner.company_id = branch
        with self.assertRaises(ValidationError):
            self.partner.ref = "123456"
        # Not the other way round.
        self.rule_model.search([]).unlink()
        self._create_rule(company_id=branch.id)
        self.partner.company_id = self.company
        self.partner.ref = "123456"
        self.assertEqual(self.partner.ref, "123456")

    def test_company_scope_falls_back_to_active_company(self):
        # A model without company_id, then one leaving it empty.
        self._create_rule(
            model_id=self.country_model.id,
            field_id=self.country_format_field.id,
            company_id=self.company.id,
        )
        country = self.env["res.country"].create({"name": "Testland", "code": "ZZ"})
        country.with_company(self.other_company).address_format = "123456"
        with self.assertRaises(ValidationError):
            country.with_company(self.company).address_format = "1234567"
        self._create_rule(company_id=self.company.id)
        self.assertFalse(self.partner.company_id)
        self.partner.with_company(self.other_company).ref = "123456"
        self.partner.ref = False
        with self.assertRaises(ValidationError):
            self.partner.with_company(self.company).ref = "123456"

    def test_record_rules_on_the_rules_themselves(self):
        branch = self.env["res.company"].create(
            {"name": "Field Length Rule Branch", "parent_id": self.company.id}
        )
        rule_a = self._create_rule(name="A", company_id=self.company.id)
        rule_b = self._create_rule(name="B", company_id=self.other_company.id)
        rule_all = self._create_rule(name="All")
        for label, company in (("company admin", self.company), ("branch", branch)):
            with self.subTest(label):
                admin = new_test_user(
                    self.env,
                    login=f"bflc_admin_{company.id}",
                    groups="base.group_user,base.group_system",
                    company_id=company.id,
                    company_ids=[Command.set(company.ids)],
                )
                visible = self.rule_model.with_user(admin).search(
                    [("id", "in", (rule_a + rule_b + rule_all).ids)]
                )
                self.assertEqual(visible, rule_a + rule_all)
        with self.assertRaises(AccessError):
            rule_a.with_user(admin).max_length = 99

    # Warning enforcement

    def test_warning_enforcement(self):
        self._create_rule(enforcement="warning")
        users = self.env.registry["res.users"]
        with (
            self.assertLogs(LOGGER, level="WARNING") as logs,
            patch.object(users, "_bus_send") as bus_send,
        ):
            self.partner.ref = "123456"
        self.assertEqual(self.partner.ref, "123456")
        self.assertIn("Field length rule violated", logs.output[0])
        notification_type, payload = bus_send.call_args[0]
        self.assertEqual(notification_type, "simple_notification")
        self.assertEqual(payload["type"], "warning")
        self.assertIn("Test Rule", payload["message"])

    def test_onchange_warning(self):
        rule = self._create_rule(enforcement="warning")
        warning = self._onchange_ref("123456")["warning"]
        self.assertEqual(warning["type"], "dialog")
        self.assertIn("Test Rule", warning["message"])
        # Within the limit, asking for defaults, and reporting another field.
        self.assertNotIn("warning", self._onchange_ref("12345"))
        self.assertNotIn("warning", self._onchange_ref("123456", field_names=()))
        self.assertNotIn(
            "warning",
            self.env["res.partner"].onchange(
                {"name": "Test Partner", "ref": "123456"},
                ["name"],
                {"name": {}, "ref": {}},
            ),
        )
        # An error rule reports itself by refusing the save.
        rule.enforcement = "error"
        self.assertNotIn("warning", self._onchange_ref("123456"))

    def test_onchange_warning_on_a_derived_value(self):
        # The value arrives in the response rather than in the values sent,
        # and on a field the client does not report as modified.
        field = self.env["ir.model.fields"]._get(
            "res.partner", "commercial_company_name"
        )
        self._create_rule(field_id=field.id, enforcement="warning")
        result = self.env["res.partner"].onchange(
            {"name": "A Very Long Company Name", "is_company": True},
            ["is_company"],
            {"name": {}, "is_company": {}, "commercial_company_name": {}},
        )
        self.assertIn("commercial_company_name", result["value"])
        self.assertIn("Test Rule", result["warning"]["message"])

    def test_onchange_warning_merges_with_another_module(self):
        # Patched below our own override, so the warning reaches us through
        # super() as another module's would.
        self._create_rule(enforcement="warning")
        original = web_models.Base.onchange

        def onchange(self, values, field_names, fields_spec):
            result = original(self, values, field_names, fields_spec)
            result["warning"] = {
                "title": "Other module",
                "message": "Other message",
                "type": "notification",
            }
            return result

        with patch.object(web_models.Base, "onchange", onchange):
            warning = self._onchange_ref("123456")["warning"]
        self.assertIn("Other message", warning["message"])
        self.assertIn("Test Rule", warning["message"])
        # Its weaker type must not demote our dialog to a toast.
        self.assertEqual(warning["type"], "dialog")

    def test_has_onchange_flag(self):
        field = self.env["res.partner"]._fields["ref"]
        self.assertFalse(self.env["res.partner"]._has_onchange(field, []))
        rule = self._create_rule()
        self.assertFalse(self.env["res.partner"]._has_onchange(field, []))
        rule.enforcement = "warning"
        self.assertTrue(self.env["res.partner"]._has_onchange(field, []))

    def test_onchange_model_id_clears_the_dependent_fields(self):
        rule = self.rule_model.new(
            {
                "model_id": self.partner_model.id,
                "field_id": self.ref_field.id,
                "condition_domain": "[('is_company', '=', True)]",
            }
        )
        rule.model_id = self.country_model
        rule._onchange_model_id()
        self.assertFalse(rule.field_id)
        self.assertFalse(rule.condition_domain)

    # Rule lifecycle

    def test_cache_invalidation(self):
        # Warmed first, or the miss would hide a missing invalidation.
        self.assertFalse(self.rule_model._get_rules("res.partner"))
        self.env.registry.cache_invalidated.clear()
        rule = self._create_rule()
        # "templates" carries the view cache, where _has_onchange is baked in.
        self.assertEqual(self.env.registry.cache_invalidated, {"default", "templates"})
        self.assertFalse(self.rule_model._get_rules("res.country"))
        with self.assertRaises(ValidationError):
            self.partner.ref = "123456"
        rule.max_length = 10
        self.partner.ref = "123456"
        rule.active = False
        self.partner.ref = "12345678901"
        # Warmed again, so the unlink has something stale to invalidate.
        rule.active = True
        self.assertTrue(self.rule_model._get_rules("res.partner"))
        rule.unlink()
        self.assertFalse(self.rule_model._get_rules("res.partner"))

    def test_archived_rule_is_not_enforced_under_active_test_false(self):
        # Without the pin, this write would cache the archived rule for every
        # later request in the worker.
        rule = self._create_rule()
        rule.active = False
        partner = self.partner.with_context(active_test=False)
        partner.ref = "123456"
        self.assertEqual(partner.ref, "123456")
        self.assertFalse(self.rule_model._get_rules("res.partner"))

    def _drift_the_condition(self, rule, condition_domain):
        """Leave the stored condition saying what the model cannot answer.

        The schema moves after the rule is saved, with nothing to check it
        again. SQL, because that is the state the database is left holding.
        """
        self.env.cr.execute(
            "UPDATE base_field_length_rule SET condition_domain = %s WHERE id = %s",
            [condition_domain, rule.id],
        )
        rule.invalidate_recordset()
        self.env.registry.clear_cache()

    def test_unusable_condition_is_skipped(self):
        # An unenforceable rule must not take every write on the model with it.
        cases = {
            "dead field": ("[('x_gone', '=', True)]", "no longer exists"),
            "across a relation": (
                "[('country_id.x_gone', '=', True)]",
                "no longer exists",
            ),
            "inside an any": (
                "[('bank_ids', 'any', [('x_gone', '=', True)])]",
                "no longer exists",
            ),
            "no longer a literal": (
                "[('date', '>=', context_today())]",
                "cannot be read",
            ),
        }
        for label, (drifted, expected) in cases.items():
            with self.subTest(label):
                rule = self._create_rule(condition_domain="[('is_company', '=', True)]")
                self._drift_the_condition(rule, drifted)
                with self.assertLogs(LOGGER, level="WARNING") as logs:
                    partner = self.env["res.partner"].create(
                        {"name": "Still Writable", "ref": "123456"}
                    )
                self.assertEqual(partner.ref, "123456")
                self.assertIn(expected, logs.output[0])
                # The audit is deliberate, so there it is reported.
                with self.assertRaisesRegex(ValidationError, "Test Rule"):
                    rule.action_check_existing_records()
                rule.unlink()

    def test_guards_against_a_module_that_is_gone(self):
        # ir.model.unlink drops the table but skips the registry reload, so the
        # override stays live with nothing behind it.
        self._create_rule()
        with patch.object(rule_module, "table_exists", return_value=False):
            self.env.registry.clear_cache()
            self.assertFalse(self.rule_model._get_rules("res.partner"))
        self.env.registry.clear_cache()
        with patch.dict(self.env.registry.models):
            self.env.registry.models.pop(self.rule_model._name)
            self.partner.ref = "123456"
        self.assertEqual(self.partner.ref, "123456")

    # Check API

    def test_validate_records(self):
        partner = self._violating_partner()
        self._create_rule()
        violations = self.rule_model.validate_records(partner, raise_on_error=False)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0]["length"], 6)
        self.assertEqual(violations[0]["max_length"], 5)
        self.assertFalse(
            self.rule_model.validate_records(
                partner, field_names=["name"], raise_on_error=False
            )
        )
        with self.assertRaises(ValidationError):
            self.rule_model.validate_records(partner)

    def test_check_value(self):
        self._create_rule(measure="byte", encoding="cp932")
        self.assertFalse(
            self.rule_model.check_value(
                "res.partner", "ref", "12345", record=self.partner
            )
        )
        with self.assertRaises(ValidationError):
            self.rule_model.check_value(
                "res.partner", "ref", "あいう", record=self.partner
            )
        violations = self.rule_model.check_value(
            "res.partner", "ref", "あいう", record=self.partner, raise_on_error=False
        )
        self.assertEqual(violations[0]["length"], 6)
        # No html extraction, whatever the type of the field.
        self._create_rule(field_id=self.comment_field.id)
        violations = self.rule_model.check_value(
            "res.partner", "comment", "<p>Hi</p>", raise_on_error=False
        )
        self.assertEqual(violations[0]["length"], 9)

    def test_check_value_resolves_the_scope(self):
        conditional = self._create_rule(condition_domain="[('is_company', '=', True)]")
        self.assertFalse(self.rule_model.check_value("res.partner", "ref", "123456"))
        self.assertFalse(
            self.rule_model.check_value(
                "res.partner", "ref", "123456", record=self.partner
            )
        )
        company_partner = self.env["res.partner"].create(
            {"name": "Company Partner", "is_company": True}
        )
        with self.assertRaises(ValidationError):
            self.rule_model.check_value(
                "res.partner", "ref", "123456", record=company_partner
            )
        conditional.write({"condition_domain": False, "company_id": self.company.id})
        self.partner.company_id = self.other_company
        rule_model = self.rule_model.with_company(self.company)
        self.assertFalse(
            rule_model.check_value("res.partner", "ref", "123456", record=self.partner)
        )
        self.assertFalse(
            self.rule_model.with_company(self.other_company).check_value(
                "res.partner", "ref", "123456"
            )
        )
        with self.assertRaises(ValidationError):
            rule_model.check_value("res.partner", "ref", "123456")

    def test_check_apis_inspect_without_side_effects(self):
        # The reads are elevated; the records handed back must not be, or
        # writing through one would bypass every ACL.
        partner = self._violating_partner().with_user(self.user)
        self._create_rule(enforcement="warning")
        rule_model = self.rule_model.with_user(self.user)
        users = self.env.registry["res.users"]
        with (
            patch.object(users, "_bus_send") as bus_send,
            self.assertNoLogs(LOGGER, level="WARNING"),
        ):
            results = (
                rule_model.validate_records(partner),
                rule_model.check_value("res.partner", "ref", "123456", record=partner),
            )
        bus_send.assert_not_called()
        for violations in results:
            record = violations[0]["record"]
            self.assertFalse(record.env.su)
            self.assertEqual(record.env.uid, self.user.id)

    # Existing records audit

    def test_action_check_existing_records(self):
        plain = self._violating_partner()
        company_partner = self._violating_partner(
            name="Company Partner", is_company=True
        )
        rule = self._create_rule(condition_domain="[('is_company', '=', True)]")
        action = rule.action_check_existing_records()
        self.assertEqual(action["res_model"], "res.partner")
        self.assertIn(company_partner.id, action["domain"][0][2])
        self.assertNotIn(plain.id, action["domain"][0][2])

    def test_audit_ignores_archiving(self):
        partner = self._violating_partner()
        archived_partner = self._violating_partner()
        archived_partner.active = False
        rule = self._create_rule()
        rule.active = False
        action = rule.action_check_existing_records()
        found = action["domain"][0][2]
        self.assertIn(partner.id, found)
        self.assertIn(archived_partner.id, found)
        # Without active_test the client's own search drops them again.
        self.assertFalse(action["context"]["active_test"])
        self.assertEqual(
            self.env[rule.model]
            .with_context(**action["context"])
            .search(action["domain"]),
            partner + archived_partner,
        )

    def test_audit_reports_what_it_may_not_read(self):
        # The method is RPC-reachable and call_kw enforces no ACL of its own.
        rule = self._create_rule()
        with self.assertRaises(AccessError):
            rule.with_user(self.user).action_check_existing_records()
        partner_class = self.env.registry["res.partner"]
        with patch.object(
            partner_class, "check_access", side_effect=AccessError("denied")
        ):
            with self.assertRaisesRegex(AccessError, "cannot audit"):
                rule.action_check_existing_records()

    def test_audit_does_not_cross_companies(self):
        # The target search is not sudo'd. ``shared`` is the positive control,
        # without which this would pass on an audit returning nothing.
        partner_b = self._violating_partner(name="Company B Partner")
        partner_b.company_id = self.other_company
        shared = self._violating_partner()
        rule = self._create_rule()
        admin_a = new_test_user(
            self.env,
            login="bflc_audit_a",
            groups="base.group_user,base.group_system",
            company_id=self.company.id,
            company_ids=[Command.set(self.company.ids)],
        )
        found = rule.with_user(admin_a).action_check_existing_records()["domain"][0][2]
        self.assertIn(shared.id, found)
        self.assertNotIn(partner_b.id, found)

    def _paged_audit(self, prefix="Paged", batch_size=3, on_first_page=None):
        """Audit nine partners in pages, optionally disturbing the data midway.

        The names run backwards on purpose: ``res.partner._order`` sorts on
        ``complete_name``, so ascending names would agree with ascending ids
        and the paging would come out right even without the explicit ``order``.
        """
        partners = self.env["res.partner"].create(
            [
                {
                    "name": f"{prefix} {8 - index}",
                    "ref": "12345" if index == 0 else "123456",
                }
                for index in range(9)
            ]
        )
        rule = self._create_rule(condition_domain=f"[('name', '=like', '{prefix} %')]")
        rule_class = self.env.registry[self.rule_model._name]
        original = rule_class._get_violations
        pages = []

        def _get_violations(model, records, specs, field_names=None, excluded_names=()):
            violations = original(model, records, specs, field_names, excluded_names)
            pages.append(records.ids)
            if len(pages) == 1 and on_first_page:
                on_first_page(partners)
            return violations

        with (
            patch.object(rule_class, "_get_violations", _get_violations),
            patch.object(rule_module, "CHECK_BATCH_SIZE", batch_size),
        ):
            action = rule.action_check_existing_records()
        return partners, action

    def test_audit_does_not_lose_a_record_when_the_rows_shift(self):
        # Paging on an offset skips the rows already seen by position, so
        # deleting one pulls everything below it up over the next offset.
        partners, action = self._paged_audit(
            on_first_page=lambda partners: partners[0].unlink()
        )
        found = action["domain"][0][2]
        self.assertEqual(len(found), len(set(found)), "a record was scanned twice")
        self.assertEqual(set(found), set(partners[1:].ids))

    @mute_logger(LOGGER)
    def test_audit_bounds_its_result(self):
        with patch.object(rule_module, "MAX_VIOLATIONS", 3):
            _partners, action = self._paged_audit(prefix="Capped")
        self.assertEqual(len(action["domain"][0][2]), 3)
        self.assertIn("First 3", action["name"])
        # Exactly eight violations: an exhaustive result, not a truncated one.
        with patch.object(rule_module, "MAX_VIOLATIONS", 8):
            partners, action = self._paged_audit(prefix="Exhaustive")
        self.assertEqual(set(action["domain"][0][2]), set(partners[1:].ids))
        self.assertNotIn("First", action["name"])

    def test_audit_reports_a_clean_result_as_such(self):
        # Otherwise this arrives as the target model's "create one" placeholder.
        # The violating fixture keeps a populated database out of the answer.
        self._violating_partner()
        rule = self._create_rule(
            condition_domain="[('name', '=like', 'No Such Partner%')]"
        )
        action = rule.action_check_existing_records()
        self.assertEqual(action["type"], "ir.actions.client")
        self.assertEqual(action["params"]["type"], "success")
        self.assertIn("Test Rule", action["params"]["message"])

    # Access rights

    def test_non_admin_gets_the_length_message(self):
        self._create_rule(name="WMS interface IF-01")
        self._cool_down()
        with self.assertRaises(ValidationError) as error:
            self.partner.with_user(self.user).ref = "123456"
        self.assertIn("WMS interface IF-01", str(error.exception))
        rule_model = self.rule_model.with_user(self.user)
        violations = rule_model.check_value(
            "res.partner", "ref", "123456", raise_on_error=False
        )
        self.assertEqual(len(violations), 1)
        with self.assertRaises(ValidationError) as error:
            rule_model.check_value("res.partner", "ref", "123456")
        self.assertIn("WMS interface IF-01", str(error.exception))

    def test_non_admin_warning_enforcement(self):
        self._create_rule(enforcement="warning")
        self._cool_down()
        result = self._onchange_ref("123456", user=self.user)
        self.assertIn("Test Rule", result["warning"]["message"])
        partner = self.partner.with_user(self.user)
        with self.assertLogs(LOGGER, level="WARNING"):
            partner.ref = "123456"
        self.assertEqual(partner.ref, "123456")

    def test_write_path_reads_through_a_relation_it_may_not_follow(self):
        # Unelevated, this would be an AccessError on the country instead.
        self.partner.country_id = self.env.ref("base.jp")
        self.env["ir.rule"].create(
            {
                "name": "No country for the test user",
                "model_id": self.country_model.id,
                "domain_force": "[(0, '=', 1)]",
                "groups": [Command.link(self.env.ref("base.group_user").id)],
            }
        )
        self._create_rule(condition_domain="[('country_id.code', '=', 'JP')]")
        self._cool_down()
        with self.assertRaises(ValidationError):
            self.partner.with_user(self.user).ref = "123456"

    def test_check_apis_read_what_the_caller_cannot(self):
        # Record rules are per operation, so a record the caller may write but
        # not read back is a state a real database reaches.
        self.env["ir.rule"].create(
            {
                "name": "No read on the test partner",
                "model_id": self.partner_model.id,
                "domain_force": f"[('id', '!=', {self.partner.id})]",
                "groups": [Command.link(self.env.ref("base.group_user").id)],
                "perm_read": True,
                "perm_write": False,
                "perm_create": False,
                "perm_unlink": False,
            }
        )
        partner = self.partner.with_user(self.user)
        rule_model = self.rule_model.with_user(self.user)
        self._create_rule(condition_domain="[('is_company', '=', True)]")
        self._cool_down()
        self.assertFalse(
            rule_model.check_value("res.partner", "ref", "123456", record=partner)
        )
        self.partner.ref = "123456"
        self._create_rule()
        self._cool_down()
        violations = rule_model.validate_records(partner, raise_on_error=False)
        self.assertEqual(len(violations), 1)
        self.assertIn("Test Partner", self.rule_model._format_violation(violations[0]))

    # Rule configuration

    def test_invalid_rule_is_refused(self):
        fields_model = self.env["ir.model.fields"]
        contact_address_field = fields_model._get("res.partner", "contact_address")
        tz_field = fields_model._get("res.partner", "tz")
        apikeys_model = self.env["ir.model"]._get("res.users.apikeys.show")
        # Each case needs its field to still have the property it was picked for.
        self.assertFalse(contact_address_field.store)
        self.assertTrue(tz_field.store)
        self.assertNotIn(tz_field.ttype, ("char", "text", "html"))
        cases = {
            "field of another model": (
                {"field_id": self.country_format_field.id},
                "does not belong to model",
            ),
            "unstored field": ({"field_id": contact_address_field.id}, "is not stored"),
            "unmeasurable field": ({"field_id": tz_field.id}, "Only char, text, html"),
            "abstract model": (
                {
                    "model_id": apikeys_model.id,
                    "field_id": fields_model._get("res.users.apikeys.show", "key").id,
                },
                "is abstract",
            ),
            "unknown encoding": (
                {"measure": "byte", "encoding": "not-an-encoding"},
                "Unknown encoding",
            ),
            "undefined codec": (
                {"measure": "byte", "encoding": "undefined"},
                "Unknown encoding",
            ),
            "unknown field in condition": (
                {"condition_domain": "[('no_such_field', '=', True)]"},
                "Invalid condition",
            ),
            "malformed condition": (
                {"condition_domain": "['bogus']"},
                "Invalid condition",
            ),
        }
        for label, (values, expected) in cases.items():
            with self.subTest(label):
                # Matched on the message, or a case passes on another branch.
                with (
                    self.assertRaisesRegex(ValidationError, expected),
                    self.cr.savepoint(),
                ):
                    self._create_rule(**values)

    @mute_logger("odoo.sql_db")
    def test_max_length_must_be_positive(self):
        with self.assertRaises(IntegrityError), self.cr.savepoint():
            self._create_rule(max_length=0)
