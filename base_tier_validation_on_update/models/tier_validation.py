# Copyright 2024 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.tools.misc import format_date, format_datetime

_logger = logging.getLogger(__name__)


class TierValidation(models.AbstractModel):
    _inherit = "tier.validation"

    on_update_message = fields.Html(
        compute="_compute_on_update_message",
        readonly=True,
    )

    @api.model
    def _get_under_validation_exceptions(self):
        fields = super()._get_under_validation_exceptions()
        return fields + ["on_update_message"]

    def _check_state_conditions(self, vals):
        if all(
            [
                review.review_on_update
                for review in self.review_ids
                if review.status == "pending"
            ]
        ) or self.env.context.get("skip_check_state_condition"):
            return False
        return super()._check_state_conditions(vals)

    # TODO rework it to avoid undesired behavior
    def write(self, vals):
        if not self._context.get("skip_on_update_check"):
            reviews_to_create = None
            reviews_and_vals = self.check_on_update_validation_required(vals)
            if isinstance(reviews_and_vals, list) and len(reviews_and_vals) == 2:
                reviews_to_create, new_vals = reviews_and_vals
            if reviews_to_create and not (
                self._context.get("skip_validation_check")
                or self._context.get("skip_on_update_check")
            ):
                if self.review_ids:
                    self.check_pending_on_update_reviews(reviews_to_create)
                self._create_on_update_reviews(reviews_to_create)
                vals = new_vals
        return super().write(vals)

    def get_required_reviews_on_update(self, tier_definitions, vals):
        reviews_to_create = []
        new_vals = vals.copy()
        for tier_definition in tier_definitions:
            if tier_definition.on_update_type in ["all", "fields"] or (
                tier_definition.on_update_type == "records"
                and self.id in tier_definition.on_update_record_ids.mapped("id")
            ):
                vals_to_review = {}
                for field, val in vals.items():
                    if (
                        field in tier_definition.on_update_field_ids.mapped("name")
                        or tier_definition.on_update_type == "all"
                    ):
                        if type(val) == list:
                            val = [
                                value
                                for value in val
                                if value[2] or (value[1] and not value[2])
                            ]
                        vals_to_review[field] = val
                        if field in new_vals:
                            new_vals.pop(field)
                if vals_to_review:
                    reviews_to_create.append({tier_definition: vals_to_review})
        return [reviews_to_create, new_vals]

    def _get_on_update_tier_definitions(self):
        return (
            self.env["tier.definition"]
            .sudo()
            .search(
                [
                    ("model_id", "=", self._name),
                    ("review_on_update", "=", True),
                    ("company_id", "in", [False] + self.env.company.ids),
                ],
                order="sequence desc",
            )
        )

    def check_on_update_validation_required(self, vals):
        definitions = self._get_on_update_tier_definitions()
        if definitions:
            return self.get_required_reviews_on_update(definitions, vals)
        return False

    def _get_on_update_error_message(self, definition):
        fields = definition.on_update_field_ids.mapped("field_description")
        fields = ", ".join(fields)
        return _(
            f"For the validation {definition.name}: You already "
            f"have pending reviews on the following fields:{fields}."
            "\n Please wait for the validation to be completed."
        )

    def check_pending_on_update_reviews(self, reviews_to_create):
        current_reviews = self.review_ids.filtered(
            lambda r: r.status == "pending" and r.review_on_update
        )
        if current_reviews:
            for review_to_create in reviews_to_create:
                for review in review_to_create.keys():
                    # Allow only one review by definition to avoid
                    # multiple write on the same values when reviews
                    # are approved.
                    if review.id in current_reviews.mapped("definition_id").ids:
                        raise ValidationError(self._get_on_update_error_message(review))

    def _notify_user(self, message):
        notification = {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Warning"),
                "type": "warning",
                "message": message,
                "sticky": True,
            },
        }
        return notification

    def _create_on_update_reviews(self, reviews_to_create):
        notifications = []
        sequence = 0
        for review in reviews_to_create:
            for definition_id, new_vals in review.items():
                fields = definition_id.on_update_field_ids.mapped("field_description")
                message = (
                    f"Validation {definition_id.name} requested for the "
                    f"following fields: {(', ').join(fields)}"
                )
                _logger.info(message)
                notifications.append(message)
                sequence += 1
                vals = []
                vals.append(self._prepare_tier_review_vals(definition_id, sequence))
                vals[0]["new_values"] = new_vals
                created_tr = self.env["tier.review"].create(vals)
                self._update_counter({"review_created": True})
                self._notify_review_requested(created_tr)
                self._notify_user(message)

    def _validate_tier(self, tiers=False):
        self.ensure_one()
        tier_reviews = tiers or self.review_ids
        user_reviews = tier_reviews.filtered(
            lambda r: r.status == "pending"
            and self.env.user in r.reviewer_ids
            and r.review_on_update
        )
        for review in user_reviews:
            review.apply_update_on_record()
        return super()._validate_tier(tiers)

    @api.model
    def _search_validated(self, operator, value):
        domain = super()._search_validated(operator, value)
        reviews = self.search([("review_ids", "!=", False)]).filtered(
            lambda r: r.validated == value
        )
        return expression.OR([domain, [("id", "in", reviews.ids)]])

    @api.model
    def _search_rejected(self, operator, value):
        domain = super()._search_validated(operator, value)
        reviews = self.search([("review_ids", "!=", False)]).filtered(
            lambda r: r.rejected == value
        )
        return expression.OR([domain, [("id", "in", reviews.ids)]])

    def _get_readable_values(self, field, field_value):
        if field.ttype == "many2one":
            field_value = self.env[field.relation].browse(field_value).display_name
        elif field.ttype == "selection":
            field_value = dict(self._fields[field.name].selection).get(field_value)
        elif field.ttype in ["one2many", "many2many"]:
            field_value = self._get_readable_m2o_m2m_values(field, field_value)
        elif field.ttype == "date":
            field_value = format_date(self.env, field_value)
        elif field.ttype == "datetime":
            field_value = format_datetime(self.env, field_value)
        return field_value

    def _compute_on_update_message(self):
        for rec in self:
            message = ""
            reviews = rec.review_ids.filtered(
                lambda r: r.review_on_update and r.status == "pending"
            )
            if reviews:
                if any(r.approve_sequence for r in reviews):
                    reviews = reviews[0]
                for review in reviews:
                    message += "<span>Modifications Requested"
                    message += f" by : {reviews[0].requested_by.name}</span>"
                    message += "<ul>"
                    message += self._add_message_review_lines(review.new_values)
                    message += "</ul>"
            if message:
                message += "</span>"
                rec.on_update_message = message
            else:
                rec.on_update_message = False

    def _add_message_review_lines(self, new_values):
        message_lines = ""
        for field_name, value in new_values.items():
            field = self.env["ir.model.fields"].search(
                [
                    ("model", "=", self._name),
                    ("name", "=", field_name),
                ],
                limit=1,
            )
            message_lines += f"<li> {field.field_description}: "
            new_value = self._get_readable_values(field, value)
            message_lines += f" {new_value}</li>"
        return message_lines

    def _format_readable_m2o_m2m_values(self, second_field, field, values):
        message_lines = ""
        current_values = []
        if second_field != field:
            current_values = (
                getattr(self, field.name)
                .filtered(
                    lambda r, v=values, k=second_field.name: v[0] in getattr(r, k).ids
                )[second_field.name]
                .ids
            )
            field_descr = f"{second_field.field_description} --> "
            model = second_field.relation
        else:
            current_values = getattr(self, field.name).ids
            field_descr = ""
            model = field.relation
        for value in values:
            value_name = self.env[model].browse(value).name
            if value not in current_values:
                message_lines += f"<li>[ADD]{field_descr} {value_name}</li>"
        deleted_values = [item for item in current_values if item not in values]
        for value in deleted_values:
            value_name = self.env[model].browse(value).name
            message_lines += f"<li>[Delete]{field_descr} {value_name}</li>"
        return message_lines

    def _get_readable_m2o_m2m_values(self, field, field_value):
        message = ""
        for record in field_value:
            if record[2] and type(record[2]) == dict:
                for field_name, second_value in record[2].items():
                    model = field.relation
                    second_field = self.env["ir.model.fields"].search(
                        [("model", "=", model), ("name", "=", field_name)],
                        limit=1,
                    )
                    if type(second_value) == int:
                        values = self._format_readable_m2o_m2m_values(
                            second_field, field, [second_value]
                        )
                        message += values + "\n"
                    elif type(second_value) == list:
                        message_line = "<ul>"
                        if type(record[1]) == int:
                            record_name = (
                                self.env[field.relation].browse(record[1]).display_name
                            )
                            message_line = record_name + ": <ul>"
                        values = self._format_readable_m2o_m2m_values(
                            second_field, field, second_value[0][2]
                        )
                        message += message_line + values + "</ul>"
            elif record[2] and type(record[2]) == list:
                message += "<ul>"
                values = self._format_readable_m2o_m2m_values(field, field, record[2])
                message += values + "</ul>"
            elif record[1] and type(record[1]) == int:
                name = self.env[field.relation].browse(record[1]).display_name
                if record[0] == 4:
                    if not record[1] in getattr(self, field.name).ids:
                        message += "[ADD] " + name
                elif record[0] in [2, 3]:
                    message += "[Delete] " + name
        return message
