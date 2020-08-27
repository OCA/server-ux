# Copyright 2020 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class TierDefinition(models.Model):
    _inherit = "tier.definition"

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

    @api.model
    def _cron_auto_tier_validation(self):
        reviews = self.env["tier.review"].search(
            [("status", "=", "pending"), ("definition_id.auto_validate", "=", True)]
        )
        for review in reviews:
            if review.status != "pending":
                continue
            doc = self.env[review.model].browse(review.res_id)
            try:
                reviewer = review.reviewer_ids or self.env.user
                if len(reviewer) > 1:
                    _logger.warn(
                        "Cannot auto tier validate %s: too many reviewers" % doc
                    )
                    continue
                review_doc = doc.with_user(reviewer)
                if review_doc.can_review:
                    review_doc._validate_tier(review)
                    review_doc._update_counter()
                    _logger.info("Auto tier validate on %s" % review_doc)
            except Exception as e:
                _logger.error("Cannot auto tier validate {}: {}".format(doc, e))
