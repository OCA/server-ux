# Copyright 2022 Le Filament (https://le-filament.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class Delegation(models.Model):
    _name = "delegation"
    _description = "Delegation"

    @api.model
    def _get_delegation_model_names(self):
        res = []
        return res

    # ------------------------------------------------------
    # Fields declaration
    # ------------------------------------------------------
    delegator_id = fields.Many2one(
        comodel_name="res.users",
        string="Delegator",
        index=True,
        required=True,
        ondelete="cascade",
        default=lambda self: self.env.user,
    )
    delegate_id = fields.Many2one(
        comodel_name="res.users",
        string="Delegate",
        index=True,
        required=True,
        ondelete="cascade",
    )
    model_id = fields.Many2one(
        comodel_name="ir.model",
        string="Delegated model",
        domain=lambda self: [("model", "in", self._get_delegation_model_names())],
    )
    model = fields.Char(related="model_id.model", index=True, store=True)
    date_start = fields.Date(
        "Start delegation date", default=fields.Datetime.today, required=True
    )
    date_end = fields.Date("End delegation date")
    sequence = fields.Integer("Sequence", default=10)
    valid = fields.Boolean("Valid", compute="_compute_valid", store=False)

    def _compute_valid(self):
        for delegation in self:
            if (
                delegation.date_start
                and delegation.date_start <= fields.Date.today()
                and (
                    not delegation.date_end
                    or delegation.date_end >= fields.Date.today()
                )
            ):
                delegation.valid = True
            else:
                delegation.valid = False

    @api.model
    def get_delegators(self, delegate_id, model):
        return (
            self.search(
                [
                    ("delegate_id", "=", delegate_id),
                    ("model_id.model", "=", model),
                ],
                order="sequence",
            )
            .filtered("valid")
            .mapped("delegator_id")
        )
