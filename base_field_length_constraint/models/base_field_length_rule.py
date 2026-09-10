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
        help="Label of the rule, shown in the error message. Use it to identify "
        "where the limit comes from, so that a violation points at the "
        "specification to fix.",
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
        help="Some systems state their limits in bytes of a given encoding "
        "rather than in characters, which makes a difference as soon as the "
        "value is not pure ASCII.",
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
        help="Warning notifies the user and writes to the log instead of "
        "blocking the write, which allows the rule to be rolled out on live "
        "data before it starts refusing values.",
    )
    message = fields.Text(
        translate=True,
        help="Custom error message. The default message is used when empty.",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        ondelete="cascade",
        help="If set, the rule only applies to the records of this company. "
        "Leave empty to apply it to all companies.",
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
                # The ORM only validates around stored writes: create passes
                # the stored names, and _compute_field_value skips a field
                # that is not stored. A rule here would never fire at all, or
                # - for the rare non-stored field carrying an inverse - fire
                # only when someone writes that field directly and never when
                # the value it derives from changes. Either way it cannot hold
                # the limit, so refuse it rather than let it look active.
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
        """Return the immutable projection of this rule used by the checks."""
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
        """Return the names whose write puts the rule back in question.

        The measured field is the obvious one, but a rule that only applies to
        part of the records reaches its scope through other fields, and a value
        that was out of scope when it was written has to be measured again the
        moment the record moves into it - a reference that was allowed to be
        long while the partner was a person is not, once it is turned into a
        company.

        A field that is not stored but inverses back into one of those names
        counts as well: the client writes ``company_type`` where the condition
        reads ``is_company``, and the inverse is what carries one to the other.
        """
        names = {field_name}
        if condition_domain:
            # Only the leading segment: what a path crosses into belongs to
            # another record, whose own writes never reach this model's
            # validation anyway.
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

        The condition is checked when the rule is saved, and the schema moves
        afterwards - a module is uninstalled, a custom field is deleted - with
        nothing to run the constraint again. Classifying that drift here rather
        than catching it later is what keeps the two apart: ``filtered_domain``
        reports a dead field with a bare ``ValueError``, which is also what a
        bug in a field's search method raises, and an unenforced limit must
        never be the way a bug reports itself.
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
            # An ``any`` carries a whole domain of its own, which iter_conditions
            # yields nothing of while the evaluation does reach into it - so a
            # field that has gone from there would surface as the very
            # ValueError this exists to forestall. That domain is read against
            # the comodel of a relation, and against this same model for ``id``,
            # which is what the loop above has left in ``model`` either way.
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

        This runs on every create and write of the model, so a rule that has
        drifted away from what it was saved against has to be dropped rather
        than raised: one unenforceable limit is a misconfiguration to correct,
        while an exception here is every write on the model refused, with an
        error naming neither the rule nor the field. Both are said out loud, and
        only once per cache fill, since the caller is memoised.
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
        """Return the active rules of ``model_name`` as immutable specs.

        This is consulted on every create and write of every model, so a model
        without any rule must cost a single dictionary lookup. Never return a
        recordset from here: the result outlives the environment it was built
        with.
        """
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
        """Return the string a rule applies to, for a stored field value.

        The stored value of an html field carries the markup, which no external
        interface ever receives, so the text it renders to is measured instead.
        The extraction approximates what the interface layer will build;
        ``check_value`` measures a given string exactly and is the precise
        answer when that matters.
        """
        if spec.ttype == "html":
            return html_to_inner_content(value)
        return value

    @api.model
    def _measure_length(self, value, measure, encoding):
        if measure != "byte":
            return len(value)
        try:
            # Unmappable characters are replaced rather than raising: reporting
            # them is a charset concern, not a length one.
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
        """Return the violations of ``specs`` on ``records`` as a list of dicts.

        ``field_names`` restricts the check to these measured fields, and
        ``excluded_names`` drops them. Which rules a write puts back in
        question is a wider question than which field it measures, and is
        answered by ``_check_records``.
        """
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
            # sudo: the reported record is deliberately bound to the caller's
            # environment, but naming it in the message must not raise.
            record=record.sudo().display_name if record else self.env._("Value"),
            field=rule.field_id.field_description,
            max_length=violation["max_length"],
            unit=unit,
            rule=rule.name,
            length=violation["length"],
        )

    @api.model
    def _notify_warnings(self, messages):
        """Push the non-blocking violations to the web client of the user.

        The notification is queued until the transaction commits, which is the
        wanted behaviour here since the value was accepted. It only reaches a
        user with an open session, so the log entry stays the reliable trace.
        """
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
        """Return the onchange warning for the fields just edited, if any.

        This warns while the value is being entered, before the write is even
        attempted, and it travels back in the onchange response rather than
        over the bus. The caller passes the non-blocking rules only.
        """
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
        """Raise the blocking violations as one error, report the others.

        A warning is only emitted once nothing blocks: raising rolls the write
        back, and a log line saying a value went through would then be false.

        :param notify: whether to log and notify the warnings. The explicit
            check methods pass ``False``: they are called to inspect values,
            and must not push a notification at the end user as a side effect
            of a caller looking something up.
        """
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
        """Check the rules that the fields just written put back in question.

        ``field_names`` are the fields the write covers and ``excluded_names``
        the ones the ORM is still inversing, both following the semantics of
        ``_validate_fields``. A rule reached through a field still being
        inversed is left to the validation that follows the inverse, since the
        record does not hold its final value yet and the scope read now would
        be the one it is leaving.
        """
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
        """Validate ``records`` against the rules defined on their model.

        For the callers that need to check records outside of a write,
        typically an interface layer about to serialize them.

        :param field_names: limit the check to these fields, all of them by default
        :param raise_on_error: return the violations instead of raising
        :return: the list of violations
        """
        if not records:
            return []
        specs = self._get_rules(records._name)
        if not specs:
            return []
        # sudo, as the write path does: evaluating a condition or naming a
        # record in the message must not raise on a caller who happens not to
        # be allowed to read what the rule looks at.
        violations = self._get_violations(records.sudo(), specs, field_names)
        if raise_on_error:
            self._report_violations(violations, notify=False)
        return violations

    @api.private
    @api.model
    def check_value(
        self, model_name, field_name, value, record=None, raise_on_error=True
    ):
        """Validate a string against the rules registered for a field.

        Values derived at serialization time - a concatenation, a split, a
        converted code - never reach a stored field, so no ORM constraint can
        protect them. Call this right before handing the value to the external
        interface, naming the field whose rules express that interface's limit.

        The string is measured exactly as given, with no html extraction: pass
        what the interface will receive.

        :param record: the single record the value derives from, used to
            evaluate the condition and the company of the rules. A rule
            carrying a condition is skipped when no record is given, since
            there is nothing to evaluate it against.
        :param raise_on_error: return the violations instead of raising
        :return: the list of violations
        """
        if record is not None:
            record.ensure_one()
            # sudo for the same reason as validate_records; reported below in
            # the caller's environment.
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
        """List the stored records that already violate the rule.

        This is what makes a rollout on live data possible: run it in warning
        mode, clean up what it returns, then switch the rule to error.
        """
        self.ensure_one()
        # Public methods are RPC-callable and call_kw enforces no ACL of its
        # own, while _to_spec() below reads the rule with elevated rights.
        self.check_access("read")
        try:
            spec = self._to_spec()
        except (ValueError, SyntaxError, TypeError) as error:
            raise self._unusable_condition_error(error) from error
        condition = spec.condition_domain or fields.Domain.TRUE
        # The condition is applied in SQL just below, so drop it from the spec
        # rather than have _get_violations re-filter every batch in memory.
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
            # One past the cap, so that a table holding exactly MAX_VIOLATIONS
            # of them is reported as the complete answer it is rather than sent
            # round a clean-up loop that never ends.
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
        """Return the action listing ``violating_ids``, or a plain all-clear.

        Without the second branch the empty result opens the target model's own
        list, whose nocontent helper invites the user to create a record - the
        opposite of what "no record violates this rule" should read like.
        """
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
            # active_test, because the scan deliberately reaches archived
            # records: an archived one still holds a value the next write has to
            # get past, and a list that silently dropped them would send the
            # user round a clean-up loop with nothing left to clean up.
            "context": {"create": False, "active_test": False},
        }
