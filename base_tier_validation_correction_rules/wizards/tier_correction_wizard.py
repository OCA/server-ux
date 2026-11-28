# Copyright 2025 Ecosoft Co., Ltd. (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command, api, fields, models


class TierCorrectionWizard(models.TransientModel):
    _name = "tier.correction.wizard"
    _description = "Tier Correction Wizard"

    res_model = fields.Char()
    res_id = fields.Integer()
    line_ids = fields.One2many(
        comodel_name="tier.correction.line.wizard",
        inverse_name="wizard_id",
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_model = self.env.context.get("active_model")
        active_id = self.env.context.get("active_id")
        if active_model and active_id:
            res["res_model"] = active_model
            res["res_id"] = active_id
            # Get pending/waiting reviews from the document
            document = self.env[active_model].browse(active_id)
            if hasattr(document, "review_ids"):
                pending_reviews = document.review_ids.filtered(
                    lambda r: r.status in ("waiting", "pending")
                )
                lines = [
                    Command.create(
                        {
                            "review_id": review.id,
                            "original_reviewer_id": review.reviewer_ids.id,
                            "new_reviewer_id": review.reviewer_ids.id,
                        },
                    )
                    for review in pending_reviews
                ]
                res["line_ids"] = lines
        return res

    def action_confirm(self):
        self.ensure_one()
        # All users can change the reviewer
        self = self.sudo()
        # Find lines where reviewers have changed
        changed_lines = self.line_ids.filtered(
            lambda line: line.original_reviewer_id != line.new_reviewer_id
        )
        if not changed_lines:
            return {"type": "ir.actions.act_window_close"}

        # Create tier.correction record
        document = self.env[self.res_model].browse(self.res_id)
        model_id = (
            self.env["ir.model"].search([("model", "=", self.res_model)], limit=1).id
        )

        correction = self.env["tier.correction"].create(
            {
                "name": f"Correction for {document.display_name}",
                "model_id": model_id,
                "correction_type": "reviewer",
                "state": "prepare",
            }
        )

        # Create tier.correction.item manually
        items_vals = [
            {
                "correction_id": correction.id,
                "res_model": self.res_model,
                "res_id": self.res_id,
                "resource_ref": f"{self.res_model},{self.res_id}",
                "reference": document.display_name,
                "new_reviewer_ids": [Command.set([line.new_reviewer_id.id])],
                "review_ids": [Command.set([line.review_id.id])],
            }
            for line in changed_lines
        ]
        self.env["tier.correction.item"].create(items_vals)

        correction.action_done()

        return {"type": "ir.actions.act_window_close"}


class TierCorrectionLineWizard(models.TransientModel):
    _name = "tier.correction.line.wizard"
    _description = "Tier Correction Line Wizard"

    wizard_id = fields.Many2one(
        comodel_name="tier.correction.wizard",
        ondelete="cascade",
        index=True,
    )
    review_id = fields.Many2one(
        comodel_name="tier.review",
    )
    original_reviewer_id = fields.Many2one(
        comodel_name="res.users",
    )
    new_reviewer_id = fields.Many2one(
        comodel_name="res.users",
    )
    allowed_reviewer_ids = fields.Many2many(
        comodel_name="res.users",
        compute="_compute_allowed_reviewer_ids",
        store=True,
    )

    def _get_allowed_reviewer_ids(self):
        """Hook method for overriding reviewer permissions.
        Override this method to customize allowed reviewers.
        """
        rules = self.env["tier.correction.rule"].search(
            [("model_id.model", "=", self.wizard_id.res_model)]
        )
        if not rules:
            return self.env["res.users"].search([])

        reviewer_line = rules.mapped("line_ids").filtered(
            lambda line: self.original_reviewer_id in line.reviewer_from_ids
        )
        return (
            reviewer_line.mapped("reviewer_to_ids")
            if reviewer_line
            else self.env["res.users"]
        )

    @api.depends("original_reviewer_id")
    def _compute_allowed_reviewer_ids(self):
        for rec in self:
            allowed = rec._get_allowed_reviewer_ids()
            rec.allowed_reviewer_ids = allowed
