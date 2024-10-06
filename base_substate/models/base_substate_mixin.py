# Copyright 2020 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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
                    _(
                        "The substate %(name)s is not defined for the state"
                        " %(state)s but for %(target_state)s "
                    )
                    % {
                        "name": rec.substate_id.name,
                        "state": _(rec_states[rec.state]),
                        "target_state": _(rec_states[target_state]),
                    }
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

        domain = [("target_state_value_id.target_state_value", "=", state_val)]
        domain += [
            ("target_state_value_id.base_substate_type_id", "=", substate_type.id)
        ]
        return domain

    def _get_default_state_value(
        self,
    ):
        """Override this method
        to change state_value
        """
        return "draft"

    def _get_substate_type(
        self,
    ):
        """Override this method
        to change substate_type (get by xml id for example)
        """
        return self.env["base.substate.type"].search(
            [("model", "=", self._name)], limit=1
        )

    substate_id = fields.Many2one(
        "base.substate",
        string="Sub State",
        ondelete="restrict",
        default=lambda self: self._get_default_substate_id(),
        tracking=5,
        index=True,
        domain=lambda self: [("model", "=", self._name)],
        copy=False,
    )

    @api.constrains("substate_id")
    def check_substate_id_consistency(self):
        for mixin_obj in self:
            if mixin_obj.substate_id and mixin_obj.substate_id.model != self._name:
                raise ValidationError(
                    _("This substate is not define for this object but for %s")
                    % mixin_obj.substate_id.model
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
            if (
                hasattr(self, "message_post_with_template")
                and substate.mail_template_id
            ):
                self.message_post_with_template(
                    substate.mail_template_id.id,
                    subtype_id=self.env["ir.model.data"]._xmlid_to_res_id(
                        "mail.mt_note"
                    ),
                )
        return values

    def write(self, values):
        values = self._update_before_write_create(values)
        res = super().write(values)
        return res

    @api.model
    def create(self, values):
        values = self._update_before_write_create(values)
        res = super().create(values)
        return res
