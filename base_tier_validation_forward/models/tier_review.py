# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class TierReview(models.Model):
    _inherit = "tier.review"
    _order = "sequence"

    status = fields.Selection(
        selection_add=[("forwarded", "Forwarded")],
    )
    sequence = fields.Float()  # change from Integer -> Float
