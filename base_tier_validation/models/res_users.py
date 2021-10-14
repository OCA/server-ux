# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, modules


class Users(models.Model):
    _inherit = 'res.users'

    review_ids = fields.Many2many(
        string="Reviews", comodel_name="tier.review"
    )

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
            reviews = self.env["tier.review"].search(review_group.get("__domain"))
            if reviews:
                records = (
                    self.env[model]
                    .sudo(self.env.user)
                    .search([("id", "in", reviews.mapped("res_id"))])
                    .filtered(lambda x: not x.rejected and x.can_review)
                )
                if len(records):
                    record = self.env[model]
                    user_reviews[model] = {
                        "name": self.env['ir.model']._get(record._name).name,
                        "model": model,
                        "icon": modules.module.get_module_icon(record._original_module),
                        "pending_count": len(records),
                    }
        return list(user_reviews.values())

    @api.model
    def get_reviews(self, data):
        review_obj = self.env['tier.review'].with_context(
            lang=self.env.user.lang)
        res = review_obj.search_read([('id', 'in', data.get('res_ids'))])
        for r in res:
            # Get the translated status value.
            r['display_status'] = dict(
                review_obj.fields_get('status')['status']['selection']
            ).get(r.get('status'))
            # Convert to datetime timezone
            if r['reviewed_date']:
                r['reviewed_date'] = \
                    fields.Datetime.context_timestamp(self, r['reviewed_date'])
        return res
