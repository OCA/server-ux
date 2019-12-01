# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CommentWizard(models.TransientModel):
    _name = "comment.wizard"
    _description = "Comment Wizard"

    object = fields.Char()
    validate_reject = fields.Char()
    res_model = fields.Char()
    res_id = fields.Integer()
    definition_ids = fields.Many2many(comodel_name="tier.definition")
    comment = fields.Char(required=True)

    def add_comment(self):
        self.ensure_one()
        rec = self.env[self.res_model].browse(self.res_id)
        user_reviews = self.env["tier.review"].search(
            [
                ("model", "=", self.res_model),
                ("res_id", "=", self.res_id),
                ("definition_id", "in", self.definition_ids.ids),
            ]
        )
        for user_review in user_reviews:
            user_review.write({"comment": self.comment})
        if self.validate_reject == "validate":
            rec._validate_tier()
        if self.validate_reject == "reject":
            rec._rejected_tier()
        rec._update_counter()
