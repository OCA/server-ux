# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class TierReview(models.Model):
    _inherit = "tier.review"

    python_reviewer_ids = fields.Many2many(
        comodel_name="res.users",
        relation="tier_review_python_reviewer_rel",
        column1="tier_review_id",
        column2="user_id",
        string="Reviewers from Python expression",
        compute="_compute_python_reviewer_ids",
        store=True,
    )

    @api.model
    def _get_reviewer_fields(self):
        res = super()._get_reviewer_fields()
        return res + ["python_reviewer_ids"]

    def _get_reviewers(self):
        return super()._get_reviewers() + self.python_reviewer_ids

    @api.depends("definition_id.reviewer_expression", "review_type", "model", "res_id")
    def _compute_python_reviewer_ids(self):
        for rec in self.filtered(lambda x: x.review_type == "expression"):
            record = rec.env[rec.model].browse(rec.res_id).exists()
            try:
                reviewer_ids = safe_eval(
                    rec.definition_id.reviewer_expression, globals_dict={"rec": record}
                )
            except Exception as error:
                raise UserError(
                    _("Error evaluating tier validation " "conditions.\n %s") % error
                )
            # Check if python expression returns 'res.users' recordset
            if (
                not isinstance(reviewer_ids, models.Model)
                or reviewer_ids._name != "res.users"
            ):
                raise UserError(
                    _(
                        "Reviewer python expression must return a "
                        "res.users recordset."
                    )
                )
            else:
                rec.python_reviewer_ids = reviewer_ids
