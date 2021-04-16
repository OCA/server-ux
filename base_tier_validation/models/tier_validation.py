# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from ast import literal_eval


class TierValidation(models.AbstractModel):
    _name = "tier.validation"
    _description = "Tier Validation (abstract)"

    _state_field = 'state'
    _state_from = ['draft']
    _state_to = ['confirmed']
    _cancel_state = 'cancel'

    # TODO: step by step validation?

    review_ids = fields.One2many(
        comodel_name='tier.review', inverse_name='res_id',
        string='Validations',
        domain=lambda self: [('model', '=', self._name)],
        auto_join=True,
    )
    validated = fields.Boolean(
        compute="_compute_validated_rejected",
        search="_search_validated",
    )
    need_validation = fields.Boolean(compute="_compute_need_validation")
    rejected = fields.Boolean(
        compute="_compute_validated_rejected", search="_search_rejected"
    )
    reviewer_ids = fields.Many2many(
        string="Reviewers", comodel_name="res.users",
        compute="_compute_reviewer_ids",
        search="_search_reviewer_ids",
    )
    can_review = fields.Boolean(
        compute="_compute_can_review", search="_search_can_review"
    )
    has_comment = fields.Boolean(
        compute='_compute_has_comment',
    )

    @api.multi
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

    @api.multi
    def _compute_can_review(self):
        for rec in self:
            rec.can_review = rec._get_sequences_to_approve(self.env.user)

    @api.model
    def _search_can_review(self, operator, value):
        res_ids = (
            self.search(
                [
                    ("review_ids.reviewer_ids", "=", self.env.user.id),
                    ("review_ids.status", "=", "pending"),
                    ("review_ids.can_review", "=", True),
                    ("rejected", "=", False),
                ]
            )
            .filtered("can_review")
            .ids
        )
        return [("id", "in", res_ids)]

    @api.multi
    @api.depends('review_ids')
    def _compute_reviewer_ids(self):
        for rec in self:
            rec.reviewer_ids = rec.review_ids.filtered(
                lambda r: r.status == 'pending').mapped('reviewer_ids')

    @api.model
    def _search_validated(self, operator, value):
        assert operator in ('=', '!='), 'Invalid domain operator'
        assert value in (True, False), 'Invalid domain value'
        pos = self.search([
            (self._state_field, 'in', self._state_from)]).filtered(
            lambda r: r.review_ids and r.validated == value)
        return [('id', 'in', pos.ids)]

    @api.model
    def _search_rejected(self, operator, value):
        assert operator in ("=", "!="), "Invalid domain operator"
        assert value in (True, False), "Invalid domain value"
        pos = self.search([(self._state_field, "in", self._state_from)]).filtered(
            lambda r: r.review_ids and r.rejected == value
        )
        return [("id", "in", pos.ids)]

    @api.model
    def _search_reviewer_ids(self, operator, value):
        reviews = self.env['tier.review'].search([
            ('model', '=', self._name),
            ('reviewer_ids', operator, value),
            ('can_review', '=', True),
            ('status', '=', 'pending')])
        return [('id', 'in', list(set(reviews.mapped('res_id'))))]

    @api.multi
    def _compute_validated_rejected(self):
        for rec in self:
            rec.validated = self._calc_reviews_validated(rec.review_ids)
            rec.rejected = self._calc_reviews_rejected(rec.review_ids)

    @api.model
    def _calc_reviews_validated(self, reviews):
        """Override for different validation policy."""
        if not reviews:
            return False
        return not any([s != 'approved' for s in reviews.mapped('status')])

    @api.model
    def _calc_reviews_rejected(self, reviews):
        """Override for different rejection policy."""
        return any([s == 'rejected' for s in reviews.mapped('status')])

    @api.multi
    def _compute_need_validation(self):
        for rec in self:
            tiers = self.env[
                'tier.definition'].search([('model', '=', self._name)])
            valid_tiers = any([rec.evaluate_tier(tier) for tier in tiers])
            rec.need_validation = not rec.review_ids and valid_tiers and \
                getattr(rec, self._state_field) in self._state_from

    @api.multi
    def evaluate_tier(self, tier):
        domain = []
        if tier.definition_domain:
            domain = literal_eval(tier.definition_domain)
        return self.search([('id', '=', self.id)] + domain)

    @api.model
    def _get_under_validation_exceptions(self):
        """Extend for more field exceptions."""
        return ['message_follower_ids', 'message_main_attachment_id', 'access_token']

    @api.multi
    def _check_allow_write_under_validation(self, vals):
        """Allow to add exceptions for fields that are allowed to be written
        even when the record is under validation."""
        exceptions = self._get_under_validation_exceptions()
        for val in vals:
            if val not in exceptions:
                return False
        return True

    @api.multi
    def write(self, vals):
        for rec in self:
            if rec._check_state_conditions(vals):
                if rec.need_validation:
                    # try to validate operation
                    reviews = rec.request_validation()
                    rec._validate_tier(reviews)
                    if not self._calc_reviews_validated(reviews):
                        raise ValidationError(_(
                            "This action needs to be validated for at least "
                            "one record. \nPlease request a validation."))
                if rec.review_ids and not rec.validated:
                    raise ValidationError(_(
                        "A validation process is still open for at least "
                        "one record."))
            if (rec.review_ids and getattr(rec, self._state_field) in
                    self._state_from and not vals.get(self._state_field) in
                    (self._state_to + [self._cancel_state]) and not
                    self._check_allow_write_under_validation(vals)):
                err_msg = _("The operation is under validation.")
                err_msg = self._add_details_to_error_message(err_msg, vals)
                raise ValidationError(err_msg)
        if vals.get(self._state_field) in self._state_from:
            self.mapped('review_ids').unlink()
        return super(TierValidation, self).write(vals)

    @api.model
    def _add_details_to_error_message(self, err_msg, vals):
        if self.env.user.has_group('base.group_no_one'):
            err_msg += "\n" + _("Cannot write fields: %s") % str(
                [self._fields[key].string for key in vals.keys()]
            )
        return err_msg

    def _check_state_conditions(self, vals):
        self.ensure_one()
        return (getattr(self, self._state_field) in self._state_from and
                vals.get(self._state_field) in self._state_to)

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
        for review in user_reviews:
            rec = self.env[review.model].browse(review.res_id)
            rec._notify_accepted_reviews()

    def _get_requested_notification_subtype(self):
        return "base_tier_validation.mt_tier_validation_requested"

    def _get_accepted_notification_subtype(self):
        return 'base_tier_validation.mt_tier_validation_accepted'

    def _get_rejected_notification_subtype(self):
        return 'base_tier_validation.mt_tier_validation_rejected'

    def _notify_accepted_reviews(self):
        if hasattr(self, 'message_post'):
            # Notify state change
            getattr(self, 'message_post')(
                subtype=self._get_accepted_notification_subtype(),
                body=self._notify_accepted_reviews_body()
            )

    def _notify_accepted_reviews_body(self):
        has_comment = self.review_ids.filtered(
            lambda r: (self.env.user in r.reviewer_ids) and r.comment)
        if has_comment:
            comment = has_comment.mapped('comment')[0]
            return _(('A review was accepted. (%s)') % (comment))
        return _('A review was accepted')

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

    @api.multi
    def validate_tier(self):
        self.ensure_one()
        sequences = self._get_sequences_to_approve(self.env.user)
        reviews = self.review_ids.filtered(lambda l: l.sequence in sequences)
        if self.has_comment:
            return self._add_comment("validate", reviews)
        self._validate_tier(reviews)
        self._update_counter()

    @api.multi
    def reject_tier(self):
        self.ensure_one()
        sequences = self._get_sequences_to_approve(self.env.user)
        reviews = self.review_ids.filtered(lambda l: l.sequence in sequences)
        if self.has_comment:
            return self._add_comment("reject", reviews)
        self._rejected_tier(reviews)
        self._update_counter()

    def _notify_rejected_review_body(self):
        has_comment = self.review_ids.filtered(
            lambda r: (self.env.user in r.reviewer_ids) and r.comment)
        if has_comment:
            comment = has_comment.mapped('comment')[0]
            return _(('A review was rejected by %s. (%s)')
                     % (self.env.user.name, comment))
        return _('A review was rejected by %s.') % (self.env.user.name)

    def _notify_rejected_review(self):
        if hasattr(self, 'message_post'):
            # Notify state change
            getattr(self, 'message_post')(
                subtype=self._get_rejected_notification_subtype(),
                body=self._notify_rejected_review_body()
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
        for review in user_reviews:
            rec = self.env[review.model].browse(review.res_id)
            rec._notify_rejected_review()

    def _notify_requested_review_body(self):
        return _('A review has been requested by %s.') % (self.env.user.name)

    def _notify_review_requested(self, tier_reviews):
        if hasattr(self, 'message_post') and \
                hasattr(self, 'message_subscribe'):
            for rec in self:
                users_to_notify = tier_reviews.filtered(
                    lambda r: r.definition_id.notify_on_create and
                    r.res_id == rec.id).mapped(
                    "reviewer_ids")
                # Subscribe reviewers and notify
                getattr(rec, 'message_subscribe')(
                    partner_ids=users_to_notify.mapped("partner_id").ids)
                getattr(rec, 'message_post')(
                    subtype=self._get_requested_notification_subtype(),
                    body=rec._notify_requested_review_body()
                )

    @api.multi
    def request_validation(self):
        td_obj = self.env['tier.definition']
        tr_obj = created_trs = self.env['tier.review']
        for rec in self:
            if getattr(rec, self._state_field) in self._state_from:
                if rec.need_validation:
                    tier_definitions = td_obj.search([
                        ('model', '=', self._name)], order="sequence desc")
                    sequence = 0
                    for td in tier_definitions:
                        if rec.evaluate_tier(td):
                            sequence += 1
                            created_trs += tr_obj.create({
                                'model': self._name,
                                'res_id': rec.id,
                                'definition_id': td.id,
                                'sequence': sequence,
                                'requested_by': self.env.uid,
                            })
                    self._update_counter()
        self._notify_review_requested(created_trs)
        return created_trs

    @api.multi
    def restart_validation(self):
        for rec in self:
            if getattr(rec, self._state_field) in self._state_from:
                rec.mapped('review_ids').unlink()
                self._update_counter()

    @api.model
    def _update_counter(self):
        self.review_ids._compute_can_review()
        notifications = []
        channel = 'base.tier.validation'
        notifications.append([channel, {}])
        self.env['bus.bus'].sendmany(notifications)

    def unlink(self):
        self.mapped('review_ids').unlink()
        return super().unlink()
