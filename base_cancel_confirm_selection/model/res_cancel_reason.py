# Copyright 2025 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCancelReason(models.Model):
    _name = "res.cancel.reason"
    _description = "Cancel Reason"

    name = fields.Char(required=True, translate=True)
    description = fields.Text(
        help="Explanation of the reason, Why we should select this reason?"
    )
    model_id = fields.Many2one(comodel_name="ir.model", string="Referenced Model")
    model = fields.Char(related="model_id.model", index=True, store=True)
    active = fields.Boolean(default=True)
