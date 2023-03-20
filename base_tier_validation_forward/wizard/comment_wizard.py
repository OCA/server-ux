# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class CommentWizard(models.TransientModel):
    _inherit = "comment.wizard"

    def add_comment(self):
        super().add_comment()
        rec = self.env[self.res_model].browse(self.res_id)
        if self.validate_reject == "forward":
            rec._forward_tier(self.review_ids)
        rec._update_counter({"review_created": True})
        return self.review_ids
