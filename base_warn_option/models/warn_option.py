# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import fields, models


class WarnOption(models.Model):
    _name = "warn.option"
    _description = "Warn Option"

    name = fields.Text(required=True, help="This text will be the warning message.")
    active = fields.Boolean(default=True)
    allowed_warning_usage = fields.Selection(
        selection=[
            ("all", "All"),
        ],
        default="all",
        required=True,
        help="Allows to choose where the message can be selected",
    )
    allowed_warning_type = fields.Selection(
        selection=[
            ("warning", "Warning"),
            ("block", "Block"),
        ],
        help="Choose the type of warning message",
    )
