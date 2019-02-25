# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class TierReview(models.Model):
    _inherit = "tier.review"

    python_reviewer_ids = fields.Many2many(
        string="Reviewers from Python expression", comodel_name="res.users",
        compute="_compute_python_reviewer_ids", store=True
    )

    @api.depends('reviewer_id', 'reviewer_group_id', 'reviewer_group_id.users',
                 'python_reviewer_ids')
    def _compute_reviewer_ids(self):
        super(TierReview, self)._compute_reviewer_ids()
        for rec in self:
            rec.reviewer_ids = rec.reviewer_id + rec.reviewer_group_id.users \
                + rec.python_reviewer_ids

    @api.multi
    @api.depends('definition_id.reviewer_expression',
                 'review_type', 'model', 'res_id')
    def _compute_python_reviewer_ids(self):
        for rec in self:
            if rec.review_type == 'expression':
                record = rec.env[rec.model].browse(rec.res_id).exists()
                try:
                    reviewer_ids = safe_eval(
                        rec.definition_id.reviewer_expression,
                        globals_dict={'rec': record})
                except Exception as error:
                    raise UserError(_(
                        "Error evaluating tier validation "
                        "conditions.\n %s") % error)
                # Check if python expression returns 'res.users' recordset
                if not isinstance(reviewer_ids, models.Model) or \
                        reviewer_ids._name != 'res.users':
                    raise UserError(_(
                        "Reviewer python expression must return a "
                        "res.users recordset."))
                else:
                    rec.python_reviewer_ids = reviewer_ids
