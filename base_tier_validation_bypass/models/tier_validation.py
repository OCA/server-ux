# Copyright 2017-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import _, fields, models
from odoo.exceptions import UserError


class TierValidation(models.AbstractModel):
    _inherit = "tier.validation"

    def _add_comment(self, validate_reject, reviews):
        self.env.ref("base_tier_validation.view_comment_wizard")
        res = super()._add_comment(validate_reject, reviews)
        if self.env.context.get("forward_bypass_only"):
            res["context"]["default_forward_reviewer_id"] = self.env.user.id
        return res

    def _get_sequences_to_approve(self, user):
        if self.env.context.get("forward_bypass_only"):
            # Bypass only the next review in sequence
            all_reviews = self.review_ids.filtered(lambda r: r.status == "pending")
            if len(all_reviews) == 1:
                raise UserError(_("Last review cannot be bypassed"))
            approve_sequences = all_reviews.filtered("approve_sequence").mapped(
                "sequence"
            )
            sequences = [min(approve_sequences)] if approve_sequences else []
            return sequences
        return super()._get_sequences_to_approve(user)

    def forward_tier(self):
        res = super().forward_tier()
        if self.env.context.get("forward_bypass_only"):
            # Change wizard view
            wizard = self.env.ref("base_tier_validation_bypass.view_bypass_wizard")
            res.update(
                {
                    "name": _("Bypass"),
                    "views": [(wizard.id, "form")],
                    "view_id": wizard.id,
                }
            )
        return res

    def _forward_tier(self, tiers=False):
        if self.env.context.get("forward_bypass_only"):
            self.ensure_one()
            if not tiers:
                raise UserError(_("There is no next review in sequence to bypass"))
            user_reviews = tiers.filtered(lambda r: r.status != "approved")
            user_reviews.write(
                {
                    "status": "forwarded",
                    "done_by": self.env.user.id,
                    "reviewed_date": fields.Datetime.now(),
                }
            )
            for review in user_reviews:
                rec = self.env[review.model].browse(review.res_id)
                rec._notify_bypassed_reviews()
            return
        super()._forward_tier(tiers=tiers)

    def _get_bypassed_notification_subtype(self):
        return "base_tier_validation_bypass.mt_tier_validation_bypassed"

    def _notify_bypassed_reviews(self):
        post = "message_post"
        if hasattr(self, post):
            getattr(self, post)(
                subtype_xmlid=self._get_bypassed_notification_subtype(),
                body=_("A review was bypassed by %s.") % (self.env.user.name),
            )
