# Copyright 2016 - Ursa Information Systems <http://ursainfosystems.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import fields, models


class IrModelAccess(models.Model):
    _inherit = "ir.model.access"

    # WARN: This can't be used in 'check()'
    # See https://github.com/odoo/odoo/blob/0b6a2569920b6584652c39b3465998649fe305b4/odoo/addons/base/models/ir_model.py#L1496  # noqa: B950
    perm_export = fields.Boolean("Export Access", default=True)
