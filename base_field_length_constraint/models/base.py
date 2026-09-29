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
        """Check the conditional rules once the record is complete.

        The ORM validates the stored fields from within ``_create``, before the
        inverse of a field like ``company_type`` has run, so a condition read
        there is read against the defaults the record is about to leave behind:
        a contact created from a menu carrying ``default_is_company`` is still
        a company at that point, whatever the user picked. Only the rules whose
        scope depends on it are held back - a plain limit is unambiguous from
        the first write, and reporting it as early as the ORM does keeps the
        error on the field the user is looking at.
        """
        specs = tuple(
            spec for spec in self._get_field_length_specs() if spec.condition_domain
        )
        if not specs:
            return super().create(vals_list)
        records = super(Base, self.with_context(**{DEFERRED_KEY: self._name})).create(
            vals_list
        )
        # Back to the caller's context, which the marker must not outlive.
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
        # sudo: a condition that reaches through a relation reads a record the
        # writer was never promised access to. Without this, a rule conditioned
        # on, say, the country of a partner turns every write of that partner
        # into an access error for anyone not allowed to read countries.
        rule_model._check_records(self.sudo(), specs, field_names, excluded_names)

    def _get_field_length_specs(self):
        """Return the length rules of this model, or an empty tuple."""
        if RULE_MODEL not in self.env.registry.models:
            return ()
        return self.env[RULE_MODEL]._get_rules(self._name)

    def _get_field_length_warning_specs(self):
        """Return the rules that warrant an onchange dialog.

        Only the non-blocking ones. An ``error`` rule already reports itself by
        refusing the save, so warning about it here would show the same message
        twice for a single edit - and twice in a row when the user saves
        straight from the field, since the client sends the onchange first.
        """
        return tuple(
            spec
            for spec in self._get_field_length_specs()
            if spec.enforcement == "warning"
        )

    def _has_onchange(self, field, other_fields):
        # The web client only sends an onchange request for the fields the view
        # marks with on_change="1", and _postprocess_on_change relies on this
        # method to decide. Without this, the warning below would never be
        # requested for a field that has no other reason to trigger an onchange.
        if super()._has_onchange(field, other_fields):
            return True
        return any(
            spec.field_name == field.name
            for spec in self._get_field_length_warning_specs()
        )

    def onchange(self, values, field_names, fields_spec):
        result = super().onchange(values, field_names, fields_spec)
        # Core answers a request naming a field the model no longer has with an
        # empty result rather than an error, so that a client holding a stale
        # view degrades quietly. Building a record out of those same values
        # below would undo that and raise on the missing field instead.
        if not result:
            return result
        # ``field_names`` is empty when the client asks for the default values
        # of a new record. Nothing has been entered yet, and the response then
        # carries every default, which the derived values below would otherwise
        # all report on.
        if not field_names:
            return result
        specs = self._get_field_length_warning_specs()
        if not specs:
            return result
        # A limit is just as often reached by a value the record derives - a
        # name pulled from a product, a reference built from a partner - as by
        # one that is typed. Those arrive in the response rather than in
        # ``values``, and the field they land on is not one the client says it
        # modified, so both have to be added for the dialog to appear at all.
        # Keyed on the fields the rules watch rather than on the type of the
        # value, so that a field the onchange has *cleared* comes through as the
        # False it now is. Filtering those out would leave the record holding
        # the over-long string the client sent and warn about a value the save
        # would never have stored.
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
        # Do not drop a warning raised by another module on the same request,
        # but do not let its title or type demote ours either: a "notification"
        # would turn the dialog into a toast that is easy to miss.
        previous = result.get("warning")
        if previous:
            warning = dict(
                warning,
                message="\n".join([previous.get("message", ""), warning["message"]]),
            )
        result["warning"] = warning
        return result
