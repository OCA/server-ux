# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class TestBinary(models.Model):

    _name = "test.binary"
    _description = "Test Binary"

    name = fields.Char(required=True)
    file = fields.Binary(attachment=True)
    file_name = fields.Char()
