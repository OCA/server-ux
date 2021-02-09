# Copyright 2020 Ecosoft - (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AffectedTierReviews(models.TransientModel):
    _name = "affected.tier.reviews"
    _description = "Show Affected Tier Reviews"

    review_ids = fields.Many2many(
        comodel_name="tier.review",
        default=lambda self: self._default_review_ids(),
    )

    def _default_review_ids(self):
        res_id = self.env.context.get("active_id")
        correction_item = self.env["tier.correction.item"].browse(res_id)
        return correction_item.review_ids.ids
