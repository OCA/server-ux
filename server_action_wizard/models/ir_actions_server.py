from odoo import fields, models


class IrActionsServer(models.Model):
    _inherit = "ir.actions.server"

    can_run_from_wizard = fields.Boolean("Can run from wizard")
    param_label_date_start = fields.Char()
    param_label_date_end = fields.Char()
    param_label_1 = fields.Char()
    param_label_2 = fields.Char()
