# Copyright 2017 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
from ast import literal_eval

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class TierDefinition(models.Model):
    _name = "tier.definition"
    _description = "Tier Definition"

    @api.model
    def _get_default_name(self):
        return _("New Tier Validation")

    @api.model
    def _get_tier_validation_model_names(self):
        res = []
        return res

    name = fields.Char(
        string="Description",
        required=True,
        default=lambda self: self._get_default_name(),
        translate=True,
    )
    model_id = fields.Many2one(
        comodel_name="ir.model",
        string="Referenced Model",
        domain=lambda self: [("model", "in", self._get_tier_validation_model_names())],
    )
    model = fields.Char(related="model_id.model", index=True, store=True)
    review_type = fields.Selection(
        string="Validated by",
        default="individual",
        selection=[
            ("individual", "Specific user"),
            ("group", "Any user in a specific group."),
        ],
    )
    reviewer_id = fields.Many2one(comodel_name="res.users", string="Reviewer")
    reviewer_group_id = fields.Many2one(
        comodel_name="res.groups", string="Reviewer group"
    )
    definition_type = fields.Selection(
        string="Definition", selection=[("domain", "Domain")], default="domain"
    )
    definition_domain = fields.Char()
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=30)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.user.company_id,
    )
    notify_on_create = fields.Boolean(
        string="Notify Reviewers on Creation",
        help="If set, all possible reviewers will be notified by email when "
        "this definition is triggered.",
    )
    has_comment = fields.Boolean(string="Comment", default=False)
    approve_sequence = fields.Boolean(
        string="Approve by sequence",
        default=False,
        help="Approval order by the specified sequence number",
    )
    server_action_id = fields.Many2one(
        comodel_name="ir.actions.server",
        string="Post Review Action",
        domain=[("usage", "=", "ir_actions_server")],
        help="Server action triggered as soon as this step is approved",
    )
    auto_validate = fields.Boolean(
        string="Auto Validate",
        help="Use schedule job to auto validate if condition is met.\n"
        "- If no user specified, use job's system user to validate\n"
        "- If 1 user matched as reviewer, use the user to validate\n"
        "- If > 1 user matched as reviewer, do not auto validate",
    )
    auto_validate_domain = fields.Char()

    @api.onchange("review_type")
    def onchange_review_type(self):
        self.reviewer_id = None
        self.reviewer_group_id = None

    def _evaluate_review(self, review):
        domain = [("id", "=", review.res_id)]
        auto_domain = review.definition_id.auto_validate_domain
        if auto_domain:
            domain += literal_eval(auto_domain)
        return self.env[review.model].search(domain)

    @api.model
    def _cron_auto_tier_validation(self):
        reviews = self.env["tier.review"].search(
            [("status", "=", "pending"), ("definition_id.auto_validate", "=", True)]
        )
        for review in reviews:
            doc = self._evaluate_review(review)
            if not doc:
                continue
            try:
                reviewer = review.reviewer_ids or self.env.user
                if len(reviewer) > 1:
                    _logger.warn(
                        "Cannot auto tier validate {}: "
                        "too many reviewers".format(doc)
                    )
                    continue
                review_doc = doc.with_user(reviewer)
                if review_doc.can_review:
                    sequences = review_doc._get_sequences_to_approve(reviewer)
                    if review.sequence in sequences:
                        review_doc._validate_tier(review)
                        review_doc._update_counter()
                        _logger.info("Auto tier validate on %s" % review_doc)
            except Exception as e:
                _logger.error("Cannot auto tier validate {}: {}".format(doc, e))
