# Copyright 2017-19 ForgeFlow S.L. (https://www.forgeflow.com)
# Copyright 2024 Moduon Team (https://www.moduon.team)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json
from ast import literal_eval

from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv.expression import OR
from odoo.tools.misc import frozendict

BASE_EXCEPTION_FIELDS = ["message_follower_ids", "access_token"]


class TierValidation(models.AbstractModel):
    _name = "tier.validation"
    _description = "Tier Validation (abstract)"

    _tier_validation_buttons_xpath = "/form/header/button[last()]"
    _tier_validation_manual_config = True

    _state_field = "state"
    _state_from = ["draft"]
    _state_to = ["confirmed"]
    _cancel_state = "cancel"

    # TODO: step by step validation?

    review_ids = fields.One2many(
        comodel_name="tier.review",
        inverse_name="res_id",
        string="Validations",
        domain=lambda self: [("model", "=", self._name)],
        auto_join=True,
    )
    to_validate_message = fields.Html(compute="_compute_validated_rejected")
    # TODO: Delete in v17 in favor of validation_status field
    validated = fields.Boolean(
        compute="_compute_validated_rejected", search="_search_validated"
    )
    validated_message = fields.Html(compute="_compute_validated_rejected")
    need_validation = fields.Boolean(compute="_compute_need_validation")
    # TODO: Delete in v17 in favor of validation_status field
    rejected = fields.Boolean(
        compute="_compute_validated_rejected", search="_search_rejected"
    )
    rejected_message = fields.Html(compute="_compute_validated_rejected")
    # Informative field (used in purchase_tier_validation), will be reliable as of v17
    validation_status = fields.Selection(
        selection=[
            ("no", "Without validation"),
            ("pending", "Pending"),
            ("rejected", "Rejected"),
            ("validated", "Validated"),
        ],
        default="no",
        compute="_compute_validation_status",
    )
    reviewer_ids = fields.Many2many(
        string="Reviewers",
        comodel_name="res.users",
        compute="_compute_reviewer_ids",
        search="_search_reviewer_ids",
    )
    can_review = fields.Boolean(
        compute="_compute_can_review", search="_search_can_review"
    )
    has_comment = fields.Boolean(compute="_compute_has_comment")
    next_review = fields.Char(compute="_compute_next_review")

    def _compute_has_comment(self):
        for rec in self:
            has_comment = rec.review_ids.filtered(
                lambda r: r.status == "pending" and (self.env.user in r.reviewer_ids)
            ).mapped("has_comment")
            rec.has_comment = True in has_comment

    def _get_sequences_to_approve(self, user):
        all_reviews = self.review_ids.filtered(lambda r: r.status == "pending")
        my_reviews = all_reviews.filtered(lambda r: user in r.reviewer_ids)
        # Include all my_reviews with approve_sequence = False
        sequences = my_reviews.filtered(lambda r: not r.approve_sequence).mapped(
            "sequence"
        )
        # Include only my_reviews with approve_sequence = True
        approve_sequences = my_reviews.filtered("approve_sequence").mapped("sequence")
        if approve_sequences:
            my_sequence = min(approve_sequences)
            min_sequence = min(all_reviews.mapped("sequence"))
            if my_sequence <= min_sequence:
                sequences.append(my_sequence)
        return sequences

    def _compute_can_review(self):
        for rec in self:
            rec.can_review = rec._get_sequences_to_approve(self.env.user)

    @api.model
    def _search_can_review(self, operator, value):
        domain = [
            ("review_ids.reviewer_ids", "=", self.env.user.id),
            ("review_ids.status", "=", "pending"),
            ("review_ids.can_review", "=", True),
            ("rejected", "=", False),
        ]
        if "active" in self._fields:
            domain.append(("active", "in", [True, False]))
        res_ids = self.search(domain).filtered("can_review").ids
        return [("id", "in", res_ids)]

    @api.depends("review_ids")
    def _compute_reviewer_ids(self):
        for rec in self:
            rec.reviewer_ids = rec.review_ids.filtered(
                lambda r: r.status == "pending"
            ).mapped("reviewer_ids")

    @api.model
    def _search_validated(self, operator, value):
        assert operator in ("=", "!="), "Invalid domain operator"
        assert value in (True, False), "Invalid domain value"
        pos = self.search(
            [(self._state_field, "in", self._state_from), ("review_ids", "!=", False)]
        ).filtered(lambda r: r.validated == value)
        return [("id", "in", pos.ids)]

    @api.model
    def _search_rejected(self, operator, value):
        assert operator in ("=", "!="), "Invalid domain operator"
        assert value in (True, False), "Invalid domain value"
        pos = self.search(
            [(self._state_field, "in", self._state_from), ("review_ids", "!=", False)]
        ).filtered(lambda r: r.rejected == value)
        return [("id", "in", pos.ids)]

    @api.model
    def _search_reviewer_ids(self, operator, value):
        model_operator = "in"
        if operator == "=" and value in ("[]", False):
            # Search for records that have not yet been through a validation
            # process.
            operator = "!="
            model_operator = "not in"
        reviews = self.env["tier.review"].search(
            [
                ("model", "=", self._name),
                ("reviewer_ids", operator, value),
                ("can_review", "=", True),
                ("status", "=", "pending"),
            ]
        )
        return [("id", model_operator, list(set(reviews.mapped("res_id"))))]

    def _get_to_validate_message_name(self):
        return self._description

    def _get_to_validate_message(self):
        return (
            """<i class="fa fa-info-circle" /> %s"""
            % _("This %s needs to be validated")
            % self._get_to_validate_message_name()
        )

    def _get_validated_message(self):
        msg = """<i class="fa fa-thumbs-up" /> %s""" % _(
            """Operation has been <b>validated</b>!"""
        )
        return self.validated and msg or ""

    def _get_rejected_message(self):
        msg = """<i class="fa fa-thumbs-down" /> %s""" % _(
            """Operation has been <b>rejected</b>."""
        )
        return self.rejected and msg or ""

    def _compute_validated_rejected(self):
        for rec in self:
            rec.validated = self._calc_reviews_validated(rec.review_ids)
            rec.validated_message = rec._get_validated_message()
            rec.rejected = self._calc_reviews_rejected(rec.review_ids)
            rec.rejected_message = rec._get_rejected_message()
            rec.to_validate_message = rec._get_to_validate_message()

    def _compute_validation_status(self):
        for item in self:
            if item.validated and not item.rejected:
                item.validation_status = "validated"
            elif not item.validated and item.rejected:
                item.validation_status = "rejected"
            elif (
                not item.validated
                and not item.rejected
                and any(item.review_ids.filtered(lambda x: x.status == "pending"))
            ):
                item.validation_status = "pending"
            else:
                item.validation_status = "no"

    def _compute_next_review(self):
        for rec in self:
            review = rec.review_ids.sorted("sequence").filtered(
                lambda l: l.status == "pending"
            )[:1]
            rec.next_review = review and _("Next: %s") % review.name or ""

    @api.model
    def _calc_reviews_validated(self, reviews):
        """Override for different validation policy."""
        if not reviews:
            return False
        return not any([s != "approved" for s in reviews.mapped("status")])

    @api.model
    def _calc_reviews_rejected(self, reviews):
        """Override for different rejection policy."""
        return any([s == "rejected" for s in reviews.mapped("status")])

    def _compute_need_validation(self):
        for rec in self:
            if isinstance(rec.id, models.NewId):
                rec.need_validation = False
                continue
            tiers = (
                self.env["tier.definition"]
                .with_context(active_test=True)
                .search(
                    [
                        ("model", "=", self._name),
                        ("company_id", "in", [False] + self.env.company.ids),
                    ]
                )
            )
            valid_tiers = any([rec.evaluate_tier(tier) for tier in tiers])
            rec.need_validation = (
                not rec.review_ids and valid_tiers and rec._check_state_from_condition()
            )

    def evaluate_tier(self, tier):
        if tier.definition_domain:
            domain = literal_eval(tier.definition_domain)
            return self.filtered_domain(domain)
        else:
            return self

    @api.model
    def _get_validation_exceptions(self, extra_domain=None, add_base_exceptions=True):
        """Return Tier Validation Exception field names that matchs custom domain."""
        exception_fields = (
            self.env["tier.validation.exception"]
            .sudo()
            .search(
                [
                    ("model_name", "=", self._name),
                    ("company_id", "in", [False] + self.env.company.ids),
                    "|",
                    ("group_ids", "in", self.env.user.groups_id.ids),
                    ("group_ids", "=", False),
                    *(extra_domain or []),
                ]
            )
            .mapped("field_ids.name")
        )
        if add_base_exceptions:
            exception_fields += BASE_EXCEPTION_FIELDS
        return list(set(exception_fields))

    @api.model
    def _get_all_validation_exceptions(self):
        """Extend for more field exceptions to be written when on the entire
        validation process."""
        return self._get_validation_exceptions()

    @api.model
    def _get_under_validation_exceptions(self):
        """Extend for more field exceptions to be written under validation."""
        return self._get_validation_exceptions(
            extra_domain=[("allowed_to_write_under_validation", "=", True)]
        )

    @api.model
    def _get_after_validation_exceptions(self):
        """Extend for more field exceptions to be written after validation."""
        return self._get_validation_exceptions(
            extra_domain=[("allowed_to_write_after_validation", "=", True)]
        )

    def _check_allow_write_under_validation(self, vals):
        """Allow to add exceptions for fields that are allowed to be written
        even when the record is under validation."""
        exceptions = self._get_under_validation_exceptions()
        for val in vals:
            if val not in exceptions:
                return False
        return True

    def _check_allow_write_after_validation(self, vals):
        """Allow to add exceptions for fields that are allowed to be written
        even when the record is after validation."""
        exceptions = self._get_after_validation_exceptions()
        for val in vals:
            if val not in exceptions:
                return False
        return True

    def _get_fields_to_write_validation(self, vals, records_exception_function):
        """Not allowed fields to write when validation depending on the given function."""
        exceptions = records_exception_function()
        not_allowed_fields = []
        for val in vals:
            if val not in exceptions:
                not_allowed_fields.append(val)
        if not not_allowed_fields:
            return []

        not_allowed_field_names, allowed_field_names = [], []
        for fld_name, fld_data in self.fields_get(
            not_allowed_fields + exceptions
        ).items():
            if fld_name in not_allowed_fields:
                not_allowed_field_names.append(fld_data["string"])
            else:
                allowed_field_names.append(fld_data["string"])
        return allowed_field_names, not_allowed_field_names

    def write(self, vals):
        for rec in self:
            if rec._check_state_conditions(vals):
                if rec.need_validation:
                    # try to validate operation
                    reviews = rec.request_validation()
                    rec._validate_tier(reviews)
                    if not self._calc_reviews_validated(reviews):
                        raise ValidationError(
                            _(
                                "This action needs to be validated for at least "
                                "one record. \nPlease request a validation."
                            )
                        )
                if rec.review_ids and not rec.validated:
                    raise ValidationError(
                        _(
                            "A validation process is still open for at least "
                            "one record."
                        )
                    )
            # Write under validation
            if (
                rec.review_ids
                and getattr(rec, self._state_field) in self._state_from
                and not vals.get(self._state_field)
                in (self._state_to + [self._cancel_state])
                and not rec._check_allow_write_under_validation(vals)
                and not rec._context.get("skip_validation_check")
            ):
                (
                    allowed_fields,
                    not_allowed_fields,
                ) = rec._get_fields_to_write_validation(
                    vals, rec._get_under_validation_exceptions
                )
                raise ValidationError(
                    _(
                        "You are not allowed to write those fields under validation.\n"
                        "- %(not_allowed_fields)s\n\n"
                        "Only those fields can be modified:\n- %(allowed_fields)s"
                    )
                    % {
                        "not_allowed_fields": "\n- ".join(not_allowed_fields),
                        "allowed_fields": "\n- ".join(allowed_fields),
                    }
                )

            # Write after validation. Check only if Tier Validation Exception is created
            if (
                rec._get_validation_exceptions(add_base_exceptions=False)
                and rec.validation_status == "validated"
                and getattr(rec, self._state_field)
                in (self._state_to + [self._cancel_state])
                and not rec._check_allow_write_after_validation(vals)
                and not rec._context.get("skip_validation_check")
            ):
                (
                    allowed_fields,
                    not_allowed_fields,
                ) = rec._get_fields_to_write_validation(
                    vals, rec._get_after_validation_exceptions
                )
                raise ValidationError(
                    _(
                        "You are not allowed to write those fields after validation.\n"
                        "- %(not_allowed_fields)s\n\n"
                        "Only those fields can be modified:\n- %(allowed_fields)s"
                    )
                    % {
                        "not_allowed_fields": "\n- ".join(not_allowed_fields),
                        "allowed_fields": "\n- ".join(allowed_fields),
                    }
                )
            if rec._allow_to_remove_reviews(vals):
                rec.mapped("review_ids").unlink()
        return super(TierValidation, self).write(vals)

    def _allow_to_remove_reviews(self, values):
        """Method for deciding whether the elimination of revisions is necessary."""
        self.ensure_one()
        state_to = values.get(self._state_field)
        if not state_to:
            return False
        state_from = self[self._state_field]
        # If you change to _cancel_state
        if state_to in (self._cancel_state):
            return True
        # If it is changed to _state_from and it was not in _state_from
        if state_to in self._state_from and state_from not in self._state_from:
            return True
        return False

    def _check_state_from_condition(self):
        return self.env.context.get("skip_check_state_condition") or (
            self._state_field in self._fields
            and getattr(self, self._state_field) in self._state_from
        )

    def _check_state_conditions(self, vals):
        self.ensure_one()
        return (
            self._check_state_from_condition()
            and vals.get(self._state_field) in self._state_to
        )

    def _validate_tier(self, tiers=False):
        self.ensure_one()
        tier_reviews = tiers or self.review_ids
        user_reviews = tier_reviews.filtered(
            lambda r: r.status == "pending" and (self.env.user in r.reviewer_ids)
        )
        user_reviews.write(
            {
                "status": "approved",
                "done_by": self.env.user.id,
                "reviewed_date": fields.Datetime.now(),
            }
        )
        reviews_to_notify = user_reviews.filtered(
            lambda r: r.definition_id.notify_on_accepted
        )
        if reviews_to_notify:
            subscribe = "message_subscribe"
            if hasattr(self, subscribe):
                getattr(self, subscribe)(
                    partner_ids=reviews_to_notify.mapped("reviewer_ids")
                    .mapped("partner_id")
                    .ids
                )
            for review in reviews_to_notify:
                rec = self.env[review.model].browse(review.res_id)
                rec._notify_accepted_reviews()

    def _get_requested_notification_subtype(self):
        return "base_tier_validation.mt_tier_validation_requested"

    def _get_accepted_notification_subtype(self):
        return "base_tier_validation.mt_tier_validation_accepted"

    def _get_rejected_notification_subtype(self):
        return "base_tier_validation.mt_tier_validation_rejected"

    def _get_restarted_notification_subtype(self):
        return "base_tier_validation.mt_tier_validation_restarted"

    def _notify_accepted_reviews(self):
        post = "message_post"
        if hasattr(self, post):
            # Notify state change
            getattr(self.sudo(), post)(
                subtype_xmlid=self._get_accepted_notification_subtype(),
                body=self._notify_accepted_reviews_body(),
            )

    def _notify_accepted_reviews_body(self):
        has_comment = self.review_ids.filtered(
            lambda r: (self.env.user in r.reviewer_ids) and r.comment
        )
        if has_comment:
            comment = has_comment.mapped("comment")[0]
            return _("A review was accepted. (%s)") % comment
        return _("A review was accepted")

    def _add_comment(self, validate_reject, reviews):
        wizard = self.env.ref("base_tier_validation.view_comment_wizard")
        return {
            "name": _("Comment"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "comment.wizard",
            "views": [(wizard.id, "form")],
            "view_id": wizard.id,
            "target": "new",
            "context": {
                "default_res_id": self.id,
                "default_res_model": self._name,
                "default_review_ids": reviews.ids,
                "default_validate_reject": validate_reject,
            },
        }

    def validate_tier(self):
        self.ensure_one()
        sequences = self._get_sequences_to_approve(self.env.user)
        reviews = self.review_ids.filtered(
            lambda l: l.sequence in sequences or l.approve_sequence_bypass
        )
        if self.has_comment:
            user_reviews = reviews.filtered(
                lambda r: r.status == "pending" and (self.env.user in r.reviewer_ids)
            )
            return self._add_comment("validate", user_reviews)
        self._validate_tier(reviews)
        self._update_counter({"review_deleted": True})

    def reject_tier(self):
        self.ensure_one()
        sequences = self._get_sequences_to_approve(self.env.user)
        reviews = self.review_ids.filtered(lambda l: l.sequence in sequences)
        if self.has_comment:
            return self._add_comment("reject", reviews)
        self._rejected_tier(reviews)
        self._update_counter({"review_deleted": True})

    def _notify_rejected_review_body(self):
        has_comment = self.review_ids.filtered(
            lambda r: (self.env.user in r.reviewer_ids) and r.comment
        )
        if has_comment:
            comment = has_comment.mapped("comment")[0]
            return _("A review was rejected by %(user)s. (%(comment)s)") % {
                "user": self.env.user.name,
                "comment": comment,
            }
        return _("A review was rejected by %s.") % (self.env.user.name)

    def _notify_rejected_review(self):
        post = "message_post"
        if hasattr(self, post):
            # Notify state change
            getattr(self.sudo(), post)(
                subtype_xmlid=self._get_rejected_notification_subtype(),
                body=self._notify_rejected_review_body(),
            )

    def _rejected_tier(self, tiers=False):
        self.ensure_one()
        tier_reviews = tiers or self.review_ids
        user_reviews = tier_reviews.filtered(
            lambda r: r.status == "pending" and (self.env.user in r.reviewer_ids)
        )
        user_reviews.write(
            {
                "status": "rejected",
                "done_by": self.env.user.id,
                "reviewed_date": fields.Datetime.now(),
            }
        )

        reviews_to_notify = user_reviews.filtered(
            lambda r: r.definition_id.notify_on_rejected
        )
        if reviews_to_notify:
            subscribe = "message_subscribe"
            if hasattr(self, subscribe):
                getattr(self, subscribe)(
                    partner_ids=reviews_to_notify.mapped("reviewer_ids")
                    .mapped("partner_id")
                    .ids
                )
            for review in reviews_to_notify:
                rec = self.env[review.model].browse(review.res_id)
                rec._notify_rejected_review()

    def _notify_requested_review_body(self):
        return _("A review has been requested by %s.") % (self.env.user.name)

    def _notify_review_requested(self, tier_reviews):
        subscribe = "message_subscribe"
        post = "message_post"
        if hasattr(self, post) and hasattr(self, subscribe):
            for rec in self.sudo():
                users_to_notify = tier_reviews.filtered(
                    lambda r: r.definition_id.notify_on_create and r.res_id == rec.id
                ).mapped("reviewer_ids")
                # Subscribe reviewers and notify
                if len(users_to_notify) > 0:
                    getattr(rec, subscribe)(
                        partner_ids=users_to_notify.mapped("partner_id").ids
                    )
                    getattr(rec, post)(
                        subtype_xmlid=self._get_requested_notification_subtype(),
                        body=rec._notify_requested_review_body(),
                    )

    def _prepare_tier_review_vals(self, definition, sequence):
        return {
            "model": self._name,
            "res_id": self.id,
            "definition_id": definition.id,
            "requested_by": self.env.uid,
            "sequence": sequence,
        }

    def request_validation(self):
        td_obj = self.env["tier.definition"]
        tr_obj = self.env["tier.review"]
        vals_list = []
        for rec in self:
            if rec._check_state_from_condition() and rec.need_validation:
                tier_definitions = td_obj.search(
                    [
                        ("model", "=", self._name),
                        ("company_id", "in", [False] + self.env.company.ids),
                    ],
                    order="sequence desc",
                )
                sequence = 0
                for td in tier_definitions:
                    if rec.evaluate_tier(td):
                        sequence += 1
                        vals_list.append(rec._prepare_tier_review_vals(td, sequence))
                self._update_counter({"review_created": True})
        created_trs = tr_obj.create(vals_list)
        self._notify_review_requested(created_trs)
        return created_trs

    def _notify_restarted_review_body(self):
        return _("The review has been reset by %s.") % (self.env.user.name)

    def _notify_restarted_review(self):
        post = "message_post"
        if hasattr(self, post):
            getattr(self.sudo(), post)(
                subtype_xmlid=self._get_restarted_notification_subtype(),
                body=self._notify_restarted_review_body(),
            )

    def restart_validation(self):
        for rec in self:
            partners_to_notify_ids = False
            if getattr(rec, self._state_field) in self._state_from:
                to_update_counter = (
                    rec.mapped("review_ids").filtered(lambda a: a.status == "pending")
                    and True
                    or False
                )
                reviews_to_notify = rec.review_ids.filtered(
                    lambda r: r.definition_id.notify_on_restarted
                )
                if reviews_to_notify:
                    partners_to_notify_ids = (
                        reviews_to_notify.mapped("reviewer_ids")
                        .mapped("partner_id")
                        .ids
                    )
                rec.mapped("review_ids").unlink()
                if to_update_counter:
                    self._update_counter({"review_deleted": True})
            if partners_to_notify_ids:
                subscribe = "message_subscribe"
                reviews_to_notify = rec.review_ids.filtered(
                    lambda r: r.definition_id.notify_on_restarted
                )
                if hasattr(self, subscribe):
                    getattr(self, subscribe)(partner_ids=partners_to_notify_ids)
                rec._notify_restarted_review()

    @api.model
    def _update_counter(self, review_counter):
        self.review_ids._compute_can_review()
        notifications = []
        channel = "base.tier.validation/updated"
        notifications.append([self.env.user.partner_id, channel, review_counter])
        self.env["bus.bus"]._sendmany(notifications)

    def unlink(self):
        self.mapped("review_ids").unlink()
        return super().unlink()

    def _add_tier_validation_buttons(self, node, params):
        str_element = self.env["ir.qweb"]._render(
            "base_tier_validation.tier_validation_buttons", params
        )
        new_node = etree.fromstring(str_element)
        return new_node

    def _add_tier_validation_label(self, node, params):
        str_element = self.env["ir.qweb"]._render(
            "base_tier_validation.tier_validation_label", params
        )
        new_node = etree.fromstring(str_element)
        return new_node

    def _add_tier_validation_reviews(self, node, params):
        str_element = self.env["ir.qweb"]._render(
            "base_tier_validation.tier_validation_reviews", params
        )
        new_node = etree.fromstring(str_element)
        return new_node

    def _get_tier_validation_readonly_domain(self):
        return [("review_ids", "!=", [])]

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        res = super().get_view(view_id=view_id, view_type=view_type, **options)
        View = self.env["ir.ui.view"]
        if view_type == "form" and not self._tier_validation_manual_config:
            doc = etree.XML(res["arch"])
            params = {
                "state_field": self._state_field,
                "state_operator": "not in",
                "state_value": self._state_from,
            }
            all_models = res["models"].copy()  # {modelname(str) ➔ fields(tuple)}
            for node in doc.xpath(self._tier_validation_buttons_xpath):
                # By default, after the last button of the header
                # _add_tier_validation_buttons process
                new_node = self._add_tier_validation_buttons(node, params)
                new_arch, new_models = View.postprocess_and_fields(new_node, self._name)
                new_node = etree.fromstring(new_arch)
                for new_element in new_node:
                    node.addnext(new_element)
                _merge_view_fields(all_models, new_models)
            for node in doc.xpath("/form/sheet"):
                # _add_tier_validation_label process
                new_node = self._add_tier_validation_label(node, params)
                new_arch, new_models = View.postprocess_and_fields(new_node, self._name)
                new_node = etree.fromstring(new_arch)
                for new_element in new_node:
                    node.addprevious(new_element)
                _merge_view_fields(all_models, new_models)
                # _add_tier_validation_reviews process
                new_node = self._add_tier_validation_reviews(node, params)
                new_arch, new_models = View.postprocess_and_fields(new_node, self._name)
                new_node = etree.fromstring(new_arch)
                node.append(new_node)
                _merge_view_fields(all_models, new_models)
            excepted_fields = self._get_all_validation_exceptions()
            for node in doc.xpath("//field[@name][not(ancestor::field)]"):
                if node.attrib.get("name") in excepted_fields:
                    continue
                modifiers = json.loads(
                    node.attrib.get("modifiers", '{"readonly": false}')
                )
                if modifiers.get("readonly") is not True:
                    modifiers["readonly"] = OR(
                        [
                            modifiers.get("readonly", []) or [],
                            self._get_tier_validation_readonly_domain(),
                        ]
                    )
                    node.attrib["modifiers"] = json.dumps(modifiers)
            res["arch"] = etree.tostring(doc)
            res["models"] = frozendict(all_models)
        return res


def _merge_view_fields(all_models: dict, new_models: dict):
    """Merge new_models into all_models. Both are {modelname(str) ➔ fields(tuple)}."""
    for model, view_fields in new_models.items():
        if model in all_models:
            all_models[model] = tuple(set(all_models[model]) | set(view_fields))
        else:
            all_models[model] = tuple(view_fields)
