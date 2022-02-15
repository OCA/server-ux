# Copyright 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, modules


class Users(models.Model):
    _inherit = "res.users"

    review_ids = fields.Many2many(string="Reviews", comodel_name="tier.review")

    @api.model
    def review_user_count(self):
        user_reviews = {}
        domain = [
            ("status", "=", "pending"),
            ("can_review", "=", True),
            ("id", "in", self.env.user.review_ids.ids),
        ]
        review_groups = self.env["tier.review"].read_group(domain, ["model"], ["model"])
        for review_group in review_groups:
            model = review_group["model"]
            Model = self.env[model]
            reviews = self.env["tier.review"].search(review_group.get("__domain"))
            # Skip Models not having Tier Validation enabled (example: was unistalled)
            if reviews and hasattr(Model, "can_review"):
                records = (
                    Model.with_user(self.env.user)
                    .with_context(active_test=False)
                    .search([("id", "in", reviews.mapped("res_id"))])
                    .filtered(lambda x: not x.rejected and x.can_review)
                )
                # Excludes any cancelled records depending on the structure of the model
                if self.env[model]._state_field in self.env[model]._fields:
                    records = records.filtered(
                        lambda x: x[x._state_field] != x._cancel_state
                    )
                if records:
                    record = self.env[model]
                    user_reviews[model] = {
                        "id": records[0].id,
                        "name": record._description,
                        "model": model,
                        "active_field": "active" in record._fields,
                        "icon": modules.module.get_module_icon(record._original_module),
                        "type": "tier_review",
                        "pending_count": len(records),
                    }
        return list(user_reviews.values())
