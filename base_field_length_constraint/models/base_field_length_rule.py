# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from ast import literal_eval
from collections import namedtuple

from odoo import api, fields, models, tools
from odoo.exceptions import AccessError, ValidationError
from odoo.tools.mail import html_to_inner_content
from odoo.tools.sql import table_exists

_logger = logging.getLogger(__name__)

MEASURABLE_TTYPES = ("char", "text", "html")
ANY_OPERATORS = ("any", "not any", "any!", "not any!")
CHECK_BATCH_SIZE = 1000
MAX_VIOLATIONS = 1000

# Immutable projection of a rule, as stored in the ormcache.
RuleSpec = namedtuple(
    "RuleSpec",
    "id field_name ttype max_length measure encoding condition_domain enforcement "
    "company_id trigger_names",
)


class BaseFieldLengthRule(models.Model):
    _name = "base.field.length.rule"
    _description = "Field Length Rule"
    _order = "model, field_id, id"

    name = fields.Char(
        required=True,
        help="Label of the rule, shown in the error message.",
    )
    model_id = fields.Many2one(
        "ir.model",
        string="Model",
        required=True,
        ondelete="cascade",
        index=True,
    )
    model = fields.Char(
        related="model_id.model", string="Model Name", store=True, index=True
    )
    field_id = fields.Many2one(
        "ir.model.fields",
        string="Field",
        required=True,
        ondelete="cascade",
        domain=f"[('model_id', '=', model_id), ('store', '=', True), "
        f"('ttype', 'in', {list(MEASURABLE_TTYPES)})]",
    )
    max_length = fields.Integer(
        required=True,
        default=1,
        help="Maximum length the value may reach, counted with the measure below.",
    )
    measure = fields.Selection(
        [("char", "Characters"), ("byte", "Bytes")],
        required=True,
        default="char",
        help="Bytes are counted in the encoding below.",
    )
    encoding = fields.Char(
        default="utf-8",
        help="Encoding used to measure the value when the measure is Bytes.",
    )
    condition_domain = fields.Char(
        string="Condition",
        help="If set, the rule only applies to the records matching this domain.",
    )
    enforcement = fields.Selection(
        [("error", "Error"), ("warning", "Warning")],
        required=True,
        default="error",
        help="Warning notifies the user and logs instead of blocking the write.",
    )
    message = fields.Text(
        translate=True,
        help="Custom error message. The default message is used when empty.",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        ondelete="cascade",
        help="If set, the rule only applies to the records of this company "
        "and its branches.",
    )
    active = fields.Boolean(default=True)

    _max_length_positive = models.Constraint(
        "CHECK(max_length > 0)",
        "The maximum length must be a positive number.",
    )

    @api.constrains("model_id", "field_id")
    def _check_field_id(self):
        for rule in self:
            if rule.model_id.abstract:
                raise ValidationError(
                    self.env._(
                        "Model '%s' is abstract, so it stores no record to check.",
                        rule.model_id.model,
                    )
                )
            if rule.field_id.model_id != rule.model_id:
                raise ValidationError(
                    self.env._(
                        "Field '%(field)s' does not belong to model '%(model)s'.",
                        field=rule.field_id.name,
                        model=rule.model_id.model,
                    )
                )
            if rule.field_id.ttype not in MEASURABLE_TTYPES:
                raise ValidationError(
                    self.env._(
                        "Field '%(field)s' is of type '%(ttype)s'. Only %(types)s "
                        "fields can be measured.",
                        field=rule.field_id.name,
                        ttype=rule.field_id.ttype,
                        types=", ".join(MEASURABLE_TTYPES),
                    )
                )
            if not rule.field_id.store:
                raise ValidationError(
                    self.env._(
                        "Field '%s' is not stored, so its value cannot be "
                        "reliably validated. Set the rule on a stored field.",
                        rule.field_id.name,
                    )
                )

    @api.constrains("measure", "encoding")
    def _check_encoding(self):
        for rule in self.filtered(lambda rule: rule.measure == "byte"):
            try:
                "Aあ".encode(rule.encoding or "", "replace")
            except (LookupError, UnicodeError) as error:
                raise ValidationError(
                    self.env._("Unknown encoding '%s'.", rule.encoding)
                ) from error

    @api.constrains("condition_domain", "model_id")
    def _check_condition_domain(self):
        for rule in self.filtered("condition_domain"):
            try:
                domain = fields.Domain(literal_eval(rule.condition_domain))
                domain.validate(self.env[rule.model_id.model])
            except Exception as error:
                raise ValidationError(
                    self.env._(
                        "Invalid condition on rule '%(rule)s': %(error)s",
                        rule=rule.name,
                        error=error,
                    )
                ) from error

    @api.onchange("model_id")
    def _onchange_model_id(self):
        self.field_id = False
        self.condition_domain = False

    def _clear_caches(self):
        self.env.registry.clear_cache("default", "templates")

    @api.model_create_multi
    def create(self, vals_list):
        rules = super().create(vals_list)
        self._clear_caches()
        return rules

    def write(self, vals):
        result = super().write(vals)
        self._clear_caches()
        return result

    def unlink(self):
        result = super().unlink()
        self._clear_caches()
        return result

    def _to_spec(self):
        self.ensure_one()
        rule = self.sudo()
        condition_domain = (
            fields.Domain(literal_eval(rule.condition_domain))
            if rule.condition_domain
            else False
        )
        return RuleSpec(
            id=rule.id,
            field_name=rule.field_id.name,
            ttype=rule.field_id.ttype,
            max_length=rule.max_length,
            measure=rule.measure,
            encoding=rule.encoding or "utf-8",
            condition_domain=condition_domain,
            enforcement=rule.enforcement,
            company_id=rule.company_id.id,
            trigger_names=self._get_trigger_names(
                rule.model, rule.field_id.name, condition_domain, rule.company_id.id
            ),
        )

    @api.model
    def _get_trigger_names(self, model_name, field_name, condition_domain, company_id):
        """Return the fields whose write must re-trigger the rule: the measured
        field, the fields of its scope, and non-stored fields inversing into them.
        """
        names = {field_name}
        if condition_domain:
            names |= {
                condition.field_expr.split(".")[0]
                for condition in condition_domain.iter_conditions()
            }
        if company_id:
            names.add("company_id")
        model = self.env[model_name]
        field_depends = self.env.registry.field_depends
        names |= {
            field.name
            for field in model._fields.values()
            if field.inverse
            and not field.store
            and not names.isdisjoint(
                depends.split(".")[0] for depends in field_depends[field]
            )
        }
        return frozenset(names)

    @api.model
    def _condition_names_a_live_field(self, model_name, domain):
        """Whether every field the condition names still exists.

        Checked up front, since a removed field and a genuine bug would both
        surface as ValueError from filtered_domain.
        """
        for condition in domain.iter_conditions():
            model = self.env[model_name]
            for name in condition.field_expr.split("."):
                field = model._fields.get(name)
                if field is None:
                    return False
                if not field.comodel_name:
                    break
                model = self.env[field.comodel_name]
            # iter_conditions() does not descend into the subdomain of 'any'.
            if condition.operator in ANY_OPERATORS and isinstance(
                condition.value, list | tuple | fields.Domain
            ):
                if not self._condition_names_a_live_field(
                    model._name, fields.Domain(condition.value)
                ):
                    return False
        return True

    @api.model
    def _get_rule_spec(self, rule, model_name):
        """Return the spec of ``rule``, or None when it cannot be enforced.

        A broken rule is logged and skipped rather than raised, so that it does
        not block every write on the model.
        """
        try:
            spec = rule._to_spec()
            usable = not spec.condition_domain or self._condition_names_a_live_field(
                model_name, spec.condition_domain
            )
        except (ValueError, SyntaxError, TypeError) as error:
            _logger.warning(
                "Skipping field length rule %s: its condition cannot be read "
                "(%s). Fix or delete the rule.",
                rule.id,
                error,
            )
            return None
        if not usable:
            _logger.warning(
                "Skipping field length rule %s: its condition %s names a field "
                "that no longer exists. Fix or delete the rule.",
                rule.id,
                spec.condition_domain,
            )
            return None
        return spec

    @api.model
    @tools.ormcache("model_name")
    def _get_rules(self, model_name):
        # Cached: never return a recordset, it would outlive its environment.
        if not table_exists(self.env.cr, self._table):
            return ()
        rules = (
            self.sudo()
            .with_context(active_test=True)
            .search([("model", "=", model_name)])
        )
        specs = (self._get_rule_spec(rule, model_name) for rule in rules)
        return tuple(spec for spec in specs if spec is not None)

    @api.model
    def _get_measurable_value(self, value, spec):
        # Html is measured on its text, without the markup.
        if spec.ttype == "html":
            return html_to_inner_content(value)
        return value

    @api.model
    def _measure_length(self, value, measure, encoding):
        if measure != "byte":
            return len(value)
        try:
            return len(value.encode(encoding, "replace"))
        except (LookupError, UnicodeError) as error:
            raise ValidationError(
                self.env._("Cannot measure a value in '%s' bytes.", encoding)
            ) from error

    @api.model
    def _rule_applies_to_company(self, spec, record):
        if not spec.company_id:
            return True
        company = record.company_id if "company_id" in record._fields else False
        company = company or self.env.company
        return spec.company_id in company.parent_ids.ids

    @api.model
    def _get_violations(self, records, specs, field_names=None, excluded_names=()):
        violations = []
        for spec in specs:
            field_name = spec.field_name
            if field_name not in records._fields:
                continue
            if field_names is not None and field_name not in field_names:
                continue
            if field_name in excluded_names:
                continue
            targets = records
            if spec.condition_domain:
                targets = targets.filtered_domain(spec.condition_domain)
            for record in targets:
                if not self._rule_applies_to_company(spec, record):
                    continue
                value = self._get_measurable_value(record[field_name], spec)
                if not value:
                    continue
                length = self._measure_length(value, spec.measure, spec.encoding)
                if length <= spec.max_length:
                    continue
                violations.append(
                    {
                        "rule_id": spec.id,
                        "record": record.with_env(self.env),
                        "field_name": field_name,
                        "length": length,
                        "max_length": spec.max_length,
                        "measure": spec.measure,
                        "enforcement": spec.enforcement,
                    }
                )
        return violations

    @api.model
    def _format_violation(self, violation):
        rule = self.sudo().browse(violation["rule_id"])
        if rule.message:
            return rule.message
        unit = (
            self.env._("bytes")
            if violation["measure"] == "byte"
            else self.env._("characters")
        )
        record = violation["record"]
        return self.env._(
            "%(record)s: '%(field)s' exceeds the limit of %(max_length)s %(unit)s "
            "set by '%(rule)s' (actual length: %(length)s).",
            record=record.sudo().display_name if record else self.env._("Value"),
            field=rule.field_id.field_description,
            max_length=violation["max_length"],
            unit=unit,
            rule=rule.name,
            length=violation["length"],
        )

    @api.model
    def _notify_warnings(self, messages):
        self.env.user._bus_send(
            "simple_notification",
            {
                "type": "warning",
                "title": self.env._("Field Length"),
                "message": "\n".join(messages),
                "sticky": True,
            },
        )

    @api.model
    def _get_onchange_warning(self, record, specs, field_names):
        violations = self._get_violations(record, specs, field_names)
        if not violations:
            return {}
        return {
            "title": self.env._("Field Length"),
            "message": "\n".join(
                self._format_violation(violation) for violation in violations
            ),
            "type": "dialog",
        }

    @api.model
    def _report_violations(self, violations, notify=True):
        """Raise the blocking violations as one error, report the others."""
        errors = []
        warnings = []
        for violation in violations:
            message = self._format_violation(violation)
            if violation["enforcement"] == "error":
                errors.append(message)
            else:
                warnings.append(message)
        if errors:
            raise ValidationError("\n".join(errors))
        if not notify or not warnings:
            return
        for message in warnings:
            _logger.warning("Field length rule violated - %s", message)
        self._notify_warnings(warnings)

    @api.model
    def _check_records(self, records, specs, field_names=None, excluded_names=()):
        # A rule triggered by a field still being inversed is left to the
        # validation that follows the inverse.
        if field_names is not None:
            specs = tuple(
                spec
                for spec in specs
                if not spec.trigger_names.isdisjoint(field_names)
                and spec.trigger_names.isdisjoint(excluded_names)
            )
        if not specs:
            return
        violations = self._get_violations(records, specs)
        if violations:
            self._report_violations(violations)

    @api.private
    @api.model
    def validate_records(self, records, field_names=None, raise_on_error=True):
        """Validate ``records`` outside of a write, e.g. before an export.

        :param field_names: limit the check to these fields
        :param raise_on_error: return the violations instead of raising
        :return: the list of violations
        """
        if not records:
            return []
        specs = self._get_rules(records._name)
        if not specs:
            return []
        violations = self._get_violations(records.sudo(), specs, field_names)
        if raise_on_error:
            self._report_violations(violations, notify=False)
        return violations

    @api.private
    @api.model
    def check_value(
        self, model_name, field_name, value, record=None, raise_on_error=True
    ):
        """Validate a string that is not stored against the rules of a field.

        The value is measured as given, with no html extraction.

        :param record: the record used to evaluate the condition and company of
            the rules; conditional rules are skipped without it
        :param raise_on_error: return the violations instead of raising
        :return: the list of violations
        """
        if record is not None:
            record.ensure_one()
            reported_record, record = record, record.sudo()
        else:
            reported_record = record
        company_holder = self.env[model_name] if record is None else record
        violations = []
        for spec in self._get_rules(model_name):
            if spec.field_name != field_name or not value:
                continue
            if spec.condition_domain and (
                record is None or not record.filtered_domain(spec.condition_domain)
            ):
                continue
            if not self._rule_applies_to_company(spec, company_holder):
                continue
            length = self._measure_length(value, spec.measure, spec.encoding)
            if length <= spec.max_length:
                continue
            violations.append(
                {
                    "rule_id": spec.id,
                    "record": reported_record,
                    "field_name": field_name,
                    "length": length,
                    "max_length": spec.max_length,
                    "measure": spec.measure,
                    "enforcement": spec.enforcement,
                }
            )
        if raise_on_error:
            self._report_violations(violations, notify=False)
        return violations

    def action_check_existing_records(self):
        self.ensure_one()
        # RPC-callable, and _to_spec() reads the rule as sudo.
        self.check_access("read")
        try:
            spec = self._to_spec()
        except (ValueError, SyntaxError, TypeError) as error:
            raise self._unusable_condition_error(error) from error
        condition = spec.condition_domain or fields.Domain.TRUE
        # The condition is applied in the search below.
        specs = (spec._replace(condition_domain=False),)
        model = self.env[self.model].with_context(active_test=False)
        try:
            model.check_access("read")
        except AccessError as error:
            raise AccessError(
                self.env._(
                    "You cannot audit '%(model)s', because you are not allowed "
                    "to read its records.",
                    model=self.model_id.display_name,
                )
            ) from error
        violating_ids = []
        last_id = 0
        while True:
            try:
                batch = model.search_fetch(
                    condition & fields.Domain("id", ">", last_id),
                    [spec.field_name],
                    limit=CHECK_BATCH_SIZE,
                    order="id",
                )
            except ValueError as error:
                raise self._unusable_condition_error(error) from error
            if not batch:
                break
            last_id = batch[-1].id
            violating_ids += [
                violation["record"].id
                for violation in self._get_violations(batch, specs)
            ]
            batch.invalidate_recordset()
            if len(violating_ids) > MAX_VIOLATIONS:
                break
        truncated = len(violating_ids) > MAX_VIOLATIONS
        del violating_ids[MAX_VIOLATIONS:]
        return self._get_audit_action(violating_ids, truncated)

    def _unusable_condition_error(self, error):
        return ValidationError(
            self.env._(
                "The condition of rule '%(rule)s' can no longer be applied to "
                "model '%(model)s': %(error)s",
                rule=self.name,
                model=self.model_id.display_name,
                error=error,
            )
        )

    def _get_audit_action(self, violating_ids, truncated=False):
        self.ensure_one()
        if not violating_ids:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "type": "success",
                    "message": self.env._("No stored record violates '%s'.", self.name),
                },
            }
        if truncated:
            _logger.warning(
                "Field length rule %s: the audit stopped at %s violations.",
                self.id,
                MAX_VIOLATIONS,
            )
        name = (
            self.env._(
                "First %(count)s records violating '%(rule)s'",
                count=MAX_VIOLATIONS,
                rule=self.name,
            )
            if truncated
            else self.env._("Records violating '%s'", self.name)
        )
        return {
            "type": "ir.actions.act_window",
            "name": name,
            "res_model": self.model,
            "view_mode": "list,form",
            "domain": [("id", "in", violating_ids)],
            # The audit includes archived records.
            "context": {"create": False, "active_test": False},
        }
