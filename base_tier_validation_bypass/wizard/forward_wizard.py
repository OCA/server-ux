# Copyright 2022 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, models


class ValidationForwardWizard(models.TransientModel):
    _inherit = "tier.validation.forward.wizard"

    def add_forward(self):
        if self.env.context.get("forward_bypass_only"):
            rec = self.env[self.res_model].browse(self.res_id)
            prev_comment = self.env["comment.wizard"].browse(
                self._context.get("comment_id")
            )
            prev_comment.write({"comment": _("Bypass: %s") % self.forward_description})
            prev_comment.add_comment()
            rec.invalidate_cache()
            rec.review_ids._compute_can_review()
            return
        super().add_forward()
