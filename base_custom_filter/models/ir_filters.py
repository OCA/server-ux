# Migrated to v14.0 by Ashish Hirpara (https://www.ashish-hirpara.com)
# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.osv import expression


class IrFilters(models.Model):
    _inherit = "ir.filters"
    _order = "model_id, sequence, name, id desc"

    def _selection_type(self):
        return [
            ("favorite", "Favorite"),
            ("filter", "Standard Filter"),
            ("groupby", "Standard Group By"),
        ]

    sequence = fields.Integer()
    type = fields.Selection(
        selection="_selection_type",
        string="Type",
        required=True,
        default="favorite",
    )
    groupby_field = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Group By Field",
        ondelete="cascade",
    )
    group_id = fields.Many2one(comodel_name="ir.filters.group", string="Filter Group")

    @api.model
    def get_filters(self, model, action_id=None):
        """We need to inject a context to obtain only the records of favorite type."""
        self = self.with_context(filter_type="favorite")
        return super().get_filters(model, action_id=action_id)

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self.env.context.get("filter_type"):
            args = expression.AND(
                (args, [("type", "=", self.env.context["filter_type"])])
            )
        return super().search(
            args, offset=offset, limit=limit, order=order, count=count
        )
