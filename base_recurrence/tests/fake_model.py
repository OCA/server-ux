# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FakeRecurrence(models.Model):

    _name = "fake.recurrence"
    _inherit = "recurrence.mixin"
    _description = "A Fake model to test recurrence mixin"

    _field_last_recurrency_date = "last_recurrency_date"
    _field_next_recurrency_date = "next_recurrency_date"

    name = fields.Char()
    recurrence_interval = fields.Integer()
    last_recurrency_date = fields.Datetime()
    next_recurrency_date = fields.Datetime()
