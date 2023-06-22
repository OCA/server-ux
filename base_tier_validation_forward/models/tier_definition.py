# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class TierDefinition(models.Model):
    _inherit = "tier.definition"

    has_forward = fields.Boolean(
        string="Allow Forward",
        default=False,
        help="Allow option to 'Forward' to different person.",
    )
