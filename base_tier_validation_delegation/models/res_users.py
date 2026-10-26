# Copyright 2026 360ERP (<https://www.360erp.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

ACCESSIBLE_FIELDS = [
    "on_holiday",
    "holiday_start_date",
    "holiday_end_date",
    "validation_replacer_id",
]


class ResUsers(models.Model):
    _inherit = "res.users"

    on_holiday = fields.Boolean(
        help="Check this box if you are out of office and want to delegate your "
        "validation tasks.",
    )
    holiday_start_date = fields.Date()
    holiday_end_date = fields.Date()
    validation_replacer_id = fields.Many2one(
        "res.users",
        string="Default Replacer",
        help="This user will receive your validation requests "
        "while you are on holiday.",
    )

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ACCESSIBLE_FIELDS

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + ACCESSIBLE_FIELDS

    @api.constrains("on_holiday", "holiday_start_date", "holiday_end_date")
    def _check_holiday_dates(self):
        """Ensure end date is not before start date."""
        for user in self:
            if (
                user.on_holiday
                and user.holiday_start_date
                and user.holiday_end_date
                and user.holiday_start_date > user.holiday_end_date
            ):
                raise ValidationError(
                    self.env._("Holiday End Date cannot be before the Start Date.")
                )

    @api.constrains("on_holiday", "validation_replacer_id")
    def _check_validation_replacer(self):
        """Ensures a user does not delegate to themselves or create a circular loop."""
        for user in self:
            if not user.on_holiday or not user.validation_replacer_id:
                continue
            if user.validation_replacer_id == user:
                raise ValidationError(
                    self.env._("You cannot delegate validation tasks to yourself.")
                )
            # Check for circular delegation (e.g., A->B->C->A)
            next_replacer = user.validation_replacer_id
            path = {user}
            while next_replacer:
                if next_replacer in path:
                    raise ValidationError(
                        self.env._("You cannot create a circular delegation path.")
                    )
                path.add(next_replacer)
                next_replacer = next_replacer.validation_replacer_id

    def _is_currently_on_holiday(self, today=None):
        """
        Checks if a user is considered on holiday right now, respecting date ranges.
        """
        self.ensure_one()
        if not today:
            today = fields.Date.context_today(self)
        return (
            self.on_holiday
            and self.validation_replacer_id
            and (not self.holiday_start_date or self.holiday_start_date <= today)
            and (not self.holiday_end_date or self.holiday_end_date >= today)
        )

    def _get_final_validation_replacer(self):
        """
        Recursively finds the final active user in a delegation chain.
        """
        self.ensure_one()
        delegation_path = {self}
        current_user = self
        today = fields.Date.context_today(self)

        while current_user._is_currently_on_holiday(today=today):
            next_user_candidate = current_user.validation_replacer_id

            if not next_user_candidate or not next_user_candidate.active:
                _logger.debug(
                    "Delegation chain broken, falling back to '%s'.", current_user.login
                )
                return current_user

            if next_user_candidate in delegation_path:
                _logger.warning(
                    "Circular delegation detected, falling back to '%s'.",
                    current_user.login,
                )
                return current_user

            delegation_path.add(next_user_candidate)
            current_user = next_user_candidate
        return current_user

    def write(self, vals):
        """
        If a user's holiday status or replacer changes, find all their pending
        reviews and trigger a re-computation of the reviewers.
        """
        holiday_fields = [
            "on_holiday",
            "holiday_start_date",
            "holiday_end_date",
            "validation_replacer_id",
        ]
        if not any(field in holiday_fields for field in vals):
            return super().write(vals)

        users_to_recompute = self

        res = super().write(vals)

        if users_to_recompute:
            self.env["tier.review"].sudo()._recompute_reviews_for_users(
                users_to_recompute
            )
        return res

    @api.model
    def _cron_update_holiday_status(self):
        """
        A daily cron job to automatically activate or deactivate a user's
        holiday status based on the configured start and end dates.
        """
        _logger.info("CRON: Running automatic holiday status update.")
        today = fields.Date.context_today(self)
        users_to_activate = self.search(
            [("on_holiday", "=", False), ("holiday_start_date", "=", today)]
        )
        if users_to_activate:
            users_to_activate.write({"on_holiday": True})
        users_to_deactivate = self.search(
            [("on_holiday", "=", True), ("holiday_end_date", "<", today)]
        )
        if users_to_deactivate:
            users_to_deactivate.write({"on_holiday": False})
        _logger.info("CRON: Finished holiday status update.")

    @api.model
    def _cron_send_delegation_reminder(self):
        """
        Sends a reminder to users whose holiday is starting soon but have not
        configured a replacer.
        """
        _logger.info("CRON: Running delegation reminder check.")
        reminder_date = fields.Date.context_today(self) + timedelta(days=3)
        users_to_remind = self.search(
            [
                ("holiday_start_date", "=", reminder_date),
                ("on_holiday", "=", False),
                ("validation_replacer_id", "=", False),
            ]
        )
        for user in users_to_remind:
            user.partner_id.message_post(
                body=self.env._(
                    "Your holiday is scheduled to start on %s. Please remember to "
                    "configure a validation replacer in your preferences to avoid "
                    "blocking any documents."
                )
                % user.holiday_start_date,
                message_type="notification",
                subtype_xmlid="mail.mt_comment",
            )
        _logger.info("CRON: Finished delegation reminder check.")
