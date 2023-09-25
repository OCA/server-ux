from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TierDefinition(models.Model):
    _inherit = "tier.definition"

    review_type = fields.Selection(selection_add=[('hr_department', 'HR Department')])
    department_id = fields.Many2one('hr.department', string="Department")
