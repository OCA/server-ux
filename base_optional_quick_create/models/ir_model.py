# Copyright 2016 ACSONE SA/NV (https://acsone.eu)
# Copyright 2016 Akretion (Alexis de Lattre alexis.delattre@akretion.com)
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError


class IrModel(models.Model):
    _inherit = "ir.model"

    avoid_quick_create = fields.Boolean()

    @staticmethod
    def _patch_method(model_obj, name, method):
        def wrapper(self, *args, **kwargs):
            return method(self, origin, *args, **kwargs)

        cls = type(model_obj)
        origin = getattr(cls, name)
        wrapper.origin = origin
        setattr(cls, name, wrapper)

    @staticmethod
    def _revert_method(model_obj, name):
        """Revert the original method called ``name`` in the given class.
        See :meth:`~._patch_method`.
        """
        cls = type(model_obj)
        method = getattr(cls, name)
        setattr(cls, name, method.origin)

    def _patch_quick_create(self):
        def _wrap_name_create():
            @api.model
            def wrapper(self, name, *args, **kwargs):
                raise UserError(
                    self.env._(
                        "Can't create %(model)s with name %(name)s quickly.\n"
                        "Please contact your system administrator to disable "
                        "this behaviour.",
                        model=self._name,
                        name=name,
                    )
                )

            return wrapper

        method_name = "name_create"
        for model in self:
            model_obj = self.env.get(model.model)
            if model.avoid_quick_create and model_obj is not None:
                self._patch_method(model_obj, method_name, _wrap_name_create())
            else:
                method = getattr(model_obj, method_name, None)
                if method and hasattr(method, "origin"):
                    self._revert_method(model_obj, method_name)
        return True

    def _register_hook(self):
        # pylint: disable=no-search-all
        models = self.search([])
        models._patch_quick_create()
        return super()._register_hook()

    @api.model_create_multi
    def create(self, vals_list):
        ir_models = super().create(vals_list)
        ir_models._patch_quick_create()
        return ir_models

    def write(self, vals):
        res = super().write(vals)
        self._patch_quick_create()
        if "avoid_quick_create" in vals:
            self.pool.registry_invalidated = True
            if self.env.registry.ready:
                self.pool.signal_changes()
        return res
