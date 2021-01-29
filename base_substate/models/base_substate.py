# Copyright 2020 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class BaseSubstateType(models.Model):
    """This model define technical data which precises
    for each target model concerned by substate,
    the technical "state" field name.
    Data in this model should be created by import as technical data
    in the specific module. For exemple in sale_subsatate we can define:
    base.substate.type:
     - name: Sale order Substate
     - model: sale.order
     - target_state_field: state
    """

    _name = "base.substate.type"
    _description = "Base Substate Type"
    _order = "name asc, model asc"

    name = fields.Char(required=True, translate=True)
    model = fields.Selection(selection=[], string="Apply on", required=True)
    target_state_field = fields.Char(
        required=True,
        help="Technical target state field name."
        ' Ex for sale order "state" for other "status" ... ',
    )


class TargetStateValue(models.Model):
    """This model define technical data that precise the translatable name
    of the target model state (ex:Quotation for 'draft' State)
    Data in this model should be created by import as technical data
    in specific module ex : sale_subsatate
    """

    _name = "target.state.value"
    _description = "Target State Value"
    _order = "name asc"

    name = fields.Char(
        "Target state Name",
        required=True,
        translate=True,
        help="Target state translateble name.\n"
        'Ex: for sale order "Quotation", "Sale order", "Locked"...',
    )
    base_substate_type_id = fields.Many2one(
        "base.substate.type",
        string="Substate Type",
        ondelete="restrict",
    )
    target_state_value = fields.Char(
        required=True,
        help="Technical target state value.\n"
        'Ex: for sale order "draft", "sale", "done", ...',
    )
    model = fields.Selection(
        related="base_substate_type_id.model",
        store=True,
        readonly=True,
        help="Model for technical use",
    )


class BaseSubstate(models.Model):
    """This model define substates that will be applied on the target model.
    for each state we can define one or more substate.
    ex:
    for the quotation state of a sale order we can define
    3 substates "In negotiation",
    "Won" and "Lost".
    We can also send mail when the susbstate is reached.
    """

    _name = "base.substate"
    _description = "Base Substate"
    _order = "active desc, sequence asc"

    name = fields.Char("Substate Name", required=True, translate=True)
    description = fields.Text(translate=True)
    sequence = fields.Integer(
        index=True,
        help="Gives the sequence order when applying the default substate",
    )
    target_state_value_id = fields.Many2one(
        "target.state.value", string="Target State Value", ondelete="restrict"
    )
    active = fields.Boolean(default=True)
    mail_template_id = fields.Many2one(
        "mail.template",
        string="Email Template",
        help="If set, an email will be sent to the partner "
        "when the object reaches this substate.",
    )
    model = fields.Selection(
        related="target_state_value_id.model",
        store=True,
        readonly=True,
        help="Model for technical use",
    )
