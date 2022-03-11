# Copyright 2020 Tecnativa - Ernesto Tejeda
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models
from odoo.tools.safe_eval import safe_eval


class ChainedSwapper(models.Model):
    _name = "chained.swapper"
    _description = "Chained Swapper"

    name = fields.Char(required=True, translate=True, index=1)
    model_id = fields.Many2one(
        comodel_name="ir.model",
        required=True,
        help="Model is used for Selecting Field. This is editable "
        "until Contextual Action is not created.",
    )
    allowed_field_ids = fields.Many2many(
        comodel_name="ir.model.fields", compute="_compute_allowed_field_ids"
    )
    field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        required=True,
        domain="[('id', 'in', allowed_field_ids)]",
    )
    sub_field_ids = fields.One2many(
        comodel_name="chained.swapper.sub.field",
        inverse_name="chained_swapper_id",
        string="Sub-fields",
    )
    constraint_ids = fields.One2many(
        comodel_name="chained.swapper.constraint",
        inverse_name="chained_swapper_id",
        string="Constraints",
    )
    ref_ir_act_window_id = fields.Many2one(
        comodel_name="ir.actions.act_window",
        string="Action",
        readonly=True,
        help="Action to make this template available on records "
        "of the related document model.",
    )
    group_ids = fields.Many2many(
        comodel_name="res.groups",
        relation="mass_group_rel",
        column1="mass_id",
        column2="group_id",
        string="Groups",
    )

    _sql_constraints = [
        (
            "model_id_field_id_unique",
            "unique (model_id, field_id)",
            "Model and Field must be unique!",
        ),
    ]

    @api.depends("model_id")
    def _compute_allowed_field_ids(self):
        model_obj = self.env["ir.model"]
        field_obj = self.env["ir.model.fields"]
        for record in self:
            allowed_field_ids = False
            if record.model_id:
                all_models = record.model_id
                active_model_obj = self.env[record.model_id.model]
                if active_model_obj._inherits:
                    keys = list(active_model_obj._inherits.keys())
                    all_models |= model_obj.search([("model", "in", keys)])
                allowed_field_ids = field_obj.search(
                    [
                        ("ttype", "not in", ["reference", "function", "one2many"]),
                        ("model_id", "in", all_models.ids),
                    ]
                )
            record.allowed_field_ids = allowed_field_ids

    @api.constrains("model_id", "field_id")
    def _check_sub_field_ids(self):
        self.mapped("sub_field_ids")._check_sub_field_chain()

    @api.onchange("model_id")
    def _onchange_model_id(self):
        self.field_id = False

    def write(self, vals):
        res = super().write(vals)
        if "name" in vals:
            self.mapped("ref_ir_act_window_id").write({"name": vals["name"]})
        return res

    def unlink(self):
        self.unlink_action()
        return super().unlink()

    def add_action(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"].create(
            {
                "name": _("Chained swap") + ": " + self.name,
                "type": "ir.actions.act_window",
                "res_model": "chained.swapper.wizard",
                "groups_id": [(4, x.id) for x in self.group_ids],
                "context": "{'chained_swapper_id': %d}" % (self.id),
                "view_mode": "form",
                "target": "new",
                "binding_model_id": self.model_id.id,
                "binding_type": "action",
            }
        )
        self.write({"ref_ir_act_window_id": action.id})
        return True

    def unlink_action(self):
        self.mapped("ref_ir_act_window_id").unlink()
        return True


class ChainedSwapperSubField(models.Model):
    _name = "chained.swapper.sub.field"
    _description = "Chained Swapper Sub-field"

    chained_swapper_id = fields.Many2one(
        comodel_name="chained.swapper", ondelete="cascade"
    )
    sub_field_chain = fields.Char(
        required=True,
        help="You can specify here a field of related fields as "
        "dotted names. Ex.: 'child_ids.lang'.",
    )

    @api.constrains("chained_swapper_id", "sub_field_chain")
    def _check_sub_field_chain(self):
        for rec in self:
            # Check sub-field exist
            try:
                chain_list = rec.sub_field_chain.split(".")
                chain_field_name = chain_list.pop()
                chain_model = self.env[rec.chained_swapper_id.model_id.model]
                for name in chain_list:
                    chain_model = chain_model[name]
                chain_model[chain_field_name]  # pylint: disable=W0104
            except KeyError:
                raise exceptions.ValidationError(
                    _("Incorrect sub-field expression:") + " " + rec.sub_field_chain
                )
            # Check sub-field and original field are the same type
            swap_field = rec.chained_swapper_id.field_id
            chain_field = self.env["ir.model.fields"].search(
                [
                    ("model_id.model", "=", chain_model._name),
                    ("name", "=", chain_field_name),
                ]
            )
            if (
                chain_field.ttype != swap_field.ttype
                or chain_field.relation != swap_field.relation
            ):
                raise exceptions.ValidationError(
                    _("The sub-field '%s' is not compatible with the main" " field.")
                    % rec.sub_field_chain
                )


class ChainedSwapperConstraint(models.Model):
    _name = "chained.swapper.constraint"
    _description = "Chained Swapper Constraint"

    chained_swapper_id = fields.Many2one(
        comodel_name="chained.swapper", ondelete="cascade"
    )
    name = fields.Char(required=True, translate=True)
    expression = fields.Text(
        string="Constraint expression",
        required=True,
        help="Boolean python expression. You can use the keyword "
        "'records' as the records selected to execute the "
        "contextual action. Ex.: bool(records.mapped('parent_id'))",
        default="True",
    )

    @api.constrains("expression")
    def _check_expression(self):
        for record in self:
            model = self.env[record.chained_swapper_id.model_id.model]
            try:
                safe_eval(record.expression, {"records": model})
            except Exception:
                raise exceptions.ValidationError(
                    _("Invalid constraint expression:" + "  " + record.expression)
                )
