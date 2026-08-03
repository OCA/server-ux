# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models

RULE_MODEL = "base.field.length.rule"
# Context key marking the model whose create is still running, see create().
DEFERRED_KEY = "base_field_length_deferred_model"


class Base(models.AbstractModel):
    _inherit = "base"

    @api.model_create_multi
    def create(self, vals_list):
        # The ORM validates stored fields before inverses (e.g. company_type)
        # have run, so conditional rules are checked once the record is complete.
        specs = tuple(
            spec for spec in self._get_field_length_specs() if spec.condition_domain
        )
        if not specs:
            return super().create(vals_list)
        records = super(Base, self.with_context(**{DEFERRED_KEY: self._name})).create(
            vals_list
        )
        records = records.with_env(self.env)
        self.env[RULE_MODEL]._check_records(records.sudo(), specs)
        return records

    def _validate_fields(self, field_names, excluded_names=()):
        specs = self._get_field_length_specs()
        if self.env.context.get(DEFERRED_KEY) == self._name:
            specs = tuple(spec for spec in specs if not spec.condition_domain)
        if not specs:
            return super()._validate_fields(field_names, excluded_names)
        field_names = set(field_names)
        excluded_names = set(excluded_names)
        super()._validate_fields(field_names, excluded_names)
        rule_model = self.env[RULE_MODEL]
        # sudo: a condition may read through a relation the user cannot access.
        rule_model._check_records(self.sudo(), specs, field_names, excluded_names)

    def _get_field_length_specs(self):
        if RULE_MODEL not in self.env.registry.models:
            return ()
        return self.env[RULE_MODEL]._get_rules(self._name)

    def _get_field_length_warning_specs(self):
        return tuple(
            spec
            for spec in self._get_field_length_specs()
            if spec.enforcement == "warning"
        )

    def _has_onchange(self, field, other_fields):
        # Make the client send an onchange for the fields under a warning rule.
        if super()._has_onchange(field, other_fields):
            return True
        return any(
            spec.field_name == field.name
            for spec in self._get_field_length_warning_specs()
        )

    def onchange(self, values, field_names, fields_spec):
        result = super().onchange(values, field_names, fields_spec)
        # An empty result means a stale view; no field_names means defaults.
        if not result or not field_names:
            return result
        specs = self._get_field_length_warning_specs()
        if not specs:
            return result
        # Also check the values the onchange itself derived.
        watched = {spec.field_name for spec in specs}
        derived = {
            name: value
            for name, value in (result.get("value") or {}).items()
            if name in watched
        }
        warning = self.env[RULE_MODEL]._get_onchange_warning(
            self.new({**values, **derived}, origin=self).sudo(),
            specs,
            set(field_names) | set(derived),
        )
        if not warning:
            return result
        # Keep another module's warning message, but keep our dialog type.
        previous = result.get("warning")
        if previous:
            warning = dict(
                warning,
                message="\n".join([previous.get("message", ""), warning["message"]]),
            )
        result["warning"] = warning
        return result
