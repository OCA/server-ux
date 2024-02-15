from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TierReview(models.Model):
    _inherit = "tier.review"

    department_id = fields.Many2one(related="definition_id.reviewer_id", readonly=True)


    def _get_reviewer_fields(self):
        fields = super(TierReview, self)._get_reviewer_fields()
        fields.append("department_id")
        return fields

    def _get_reviewers(self):
        reviewers = super(TierReview, self)._get_reviewers()
        if self.review_type == 'hr_department' and self.definition_id.department_id:
            # Obtener todos los usuarios del departamento especificado
            department_users = self.env['res.users'].search([('department_id', '=', self.definition_id.department_id.id)])
            reviewers |= department_users
        return reviewers
