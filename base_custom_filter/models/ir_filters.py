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
            ("search", "Search"),
            ("filter", "Standard Filter"),
            ("groupby", "Standard Group By"),
        ]

    sequence = fields.Integer()
    type = fields.Selection(
        selection="_selection_type",
        required=True,
        default="favorite",
    )
    search_field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        ondelete="cascade",
    )
    groupby_field = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Group By Field",
        ondelete="cascade",
    )
    filter_domain = fields.Text(
        help="""Enter a filter domain expression if necessary.
        Example: [('default_code', 'ilike', self)]"""
    )
    group_ids = fields.Many2many("res.groups", string="User Groups")
    group_id = fields.Many2one(comodel_name="ir.filters.group", string="Filter Group")

    @api.model
    def get_filters(
        self,
        model,
        action_id=None,
        embedded_action_id=None,
        embedded_parent_res_id=None,
    ):
        """We need to inject a context to obtain only the records of favorite type."""
        self = self.with_context(filter_type="favorite")
        return super().get_filters(
            model, action_id, embedded_action_id, embedded_parent_res_id
        )

    @api.model
    @api.returns("self")
    def search(self, domain, offset=0, limit=None, order=None):
        if self.env.context.get("filter_type"):
            domain = expression.AND(
                (domain, [("type", "=", self.env.context["filter_type"])])
            )
        return super().search(domain, offset, limit, order)
