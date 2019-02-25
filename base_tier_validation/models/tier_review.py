# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class TierReview(models.Model):
    _name = "tier.review"

    name = fields.Char(related="definition_id.name", readonly=True)
    status = fields.Selection(
        selection=[("pending", "Pending"),
                   ("rejected", "Rejected"),
                   ("approved", "Approved")],
        default="pending",
    )
    model = fields.Char(string='Related Document Model', index=True)
    res_id = fields.Integer(string='Related Document ID', index=True)
    definition_id = fields.Many2one(
        comodel_name="tier.definition",
    )
    review_type = fields.Selection(
        related="definition_id.review_type", readonly=True,
    )
    reviewer_id = fields.Many2one(
        related="definition_id.reviewer_id", readonly=True,
    )
    reviewer_group_id = fields.Many2one(
        related="definition_id.reviewer_group_id", readonly=True,
    )
    python_reviewer_ids = fields.Many2many(
        string="Reviewers from Python expression", comodel_name="res.users",
        compute="_compute_python_reviewer_ids", store=True
    )
    reviewer_ids = fields.Many2many(
        string="Reviewers", comodel_name="res.users",
        compute="_compute_reviewer_ids", store=True,
    )
    sequence = fields.Integer(string="Tier")
    done_by = fields.Many2one(
        comodel_name="res.users",
    )
    requested_by = fields.Many2one(
        comodel_name="res.users",
    )

    @api.multi
    @api.depends('reviewer_id', 'reviewer_group_id', 'reviewer_group_id.users',
                 'python_reviewer_ids')
    def _compute_reviewer_ids(self):
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
