# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TierDefinition(models.Model):
    _inherit = "tier.definition"

    python_code = fields.Text(
        string="Tier Definition Expression",
        help="Write Python code that defines when this tier confirmation "
        "will be needed. The result of executing the expresion must be "
        "a boolean.",
        default="""# Available locals:\n#  - rec: current record""",
    )
    definition_type = fields.Selection(selection_add=[("formula", "Formula")])
    reviewer_expression = fields.Text(
        string="Review Expression",
        help="Write Python code that defines the reviewer. "
        "The result of executing the expression must be a res.users "
        "recordset.",
        default="# Available locals:\n#  - rec: current record\n"
        "#  - Expects a recordset of res.users",
    )
    review_type = fields.Selection(selection_add=[("expression", "Python Expression")])

    @api.onchange("review_type")
    def onchange_review_type(self):
        super(TierDefinition, self).onchange_review_type()
        self.reviewer_expression = False
        if self.review_type == "expression":
            self.reviewer_expression = (
                "# Available locals:\n"
                "#  - rec: current record\n"
                "#  - Expects a recordset of res.users"
            )
