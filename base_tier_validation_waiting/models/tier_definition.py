# Copyright (c) 2022 brain-tec AG (https://braintec.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class TierDefinition(models.Model):
    _inherit = "tier.definition"

    notify_on_pending = fields.Boolean(
        string="Notify Reviewers on reaching Pending",
        help="If set, all possible reviewers will be notified by email when "
        "this definition is triggered.",
    )
