# Copyright 2020 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.fields import Domain


class BaseSubstateMixin(models.AbstractModel):
    _name = "base.substate.mixin"
    _description = "BaseSubstate Mixin"
    _state_field = "state"

    @api.constrains("substate_id", _state_field)
    def check_substate_id_value(self):
        rec_states = dict(self._fields[self._state_field].selection)
        for rec in self:
            target_state = rec.substate_id.target_state_value_id.target_state_value
            if rec.substate_id and rec.state != target_state:
                raise ValidationError(
                    self.env._(
                        "Substate %(substate_name)s not defined for "
                        "state %(state_name)s but for %(target_state_name)s",
                        substate_name=rec.substate_id.name,
                        state_name=rec_states[rec.state],
                        target_state_name=rec_states[target_state],
                    )
                )

    def _get_default_substate_id(self, state_val=False):
        """Gives default substate_id"""
        search_domain = self._get_default_substate_domain(state_val)
        # perform search, return the first found
        return (
            self.env["base.substate"]
            .search(search_domain, order="sequence", limit=1)
            .id
        )

    def _get_default_substate_domain(self, state_val=False):
        """Override this method
        to change domain values
        """
        if not state_val:
            state_val = self._get_default_state_value()
        substate_type = self._get_substate_type()
        state_field = substate_type.target_state_field
        if self and not state_val and state_field in self._fields:
            state_val = self[state_field]

        domain = Domain(
            "target_state_value_id.target_state_value", "=", state_val
        ) & Domain("target_state_value_id.base_substate_type_id", "=", substate_type.id)
        return domain

    def _get_default_state_value(self):
        """Override this method to change state_value"""
        return "draft"

    def _get_substate_type(self):
        """Override this method to change substate_type (get by xml id for example)"""
        return self.env["base.substate.type"].search(
            Domain("model", "=", self._name), limit=1
        )

    substate_id = fields.Many2one(
        "base.substate",
        string="Sub State",
        ondelete="restrict",
        default=lambda self: self._get_default_substate_id(),
        index=True,
        domain=lambda self: Domain("model", "=", self._name),
        copy=False,
        tracking=True,
    )

    @api.constrains("substate_id")
    def check_substate_id_consistency(self):
        for mixin_obj in self:
            if mixin_obj.substate_id and mixin_obj.substate_id.model != self._name:
                raise ValidationError(
                    self.env._(
                        "Substate not for this object but for %(model_name)s",
                        model_name=mixin_obj.substate_id.model,
                    )
                )

    def _update_before_write_create(self, values):
        substate_type = self._get_substate_type()
        state_field = substate_type.target_state_field
        if values.get(state_field) and not values.get("substate_id"):
            state_val = values.get(state_field)
            values["substate_id"] = self._get_default_substate_id(state_val)
        # Send mail if substate has mail template
        if values.get("substate_id"):
            substate = self.env["base.substate"].browse(values["substate_id"])
            if hasattr(self, "message_post_with_source") and substate.mail_template_id:
                self.message_post_with_source(
                    substate.mail_template_id,
                    message_type="comment",
                    subtype_id=self.env["ir.model.data"]._xmlid_to_res_id(
                        "mail.mt_note"
                    ),
                )
        return values

    def write(self, values):
        values = self._update_before_write_create(values)
        res = super().write(values)
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals = self._update_before_write_create(vals)
        res = super().create(vals_list)
        return res
