# Copyright 2016 ACSONE SA/NV (https://acsone.eu)
# Copyright 2016 Akretion (Alexis de Lattre alexis.delattre@akretion.com)
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class IrModel(models.Model):
    _inherit = "ir.model"

    avoid_quick_create = fields.Boolean()

    # brought back these methods `_patch_method` and `_revert_method`
    # From this following PR these methods are removed since
    # there is no any proper use for these methods in odoo.
    # refer this bellow PR for more info.
    # https://github.com/odoo/odoo/pull/110370
    # But since we use this to patch the original_method
    # I added back again.
    @staticmethod
    def _patch_method(model_obj, name, method):
        """Monkey-patch a method for all instances of this model. This replaces
        the method called ``name`` by ``method`` in the given class.
        The original method is then accessible via ``method.origin``, and it
        can be restored with :meth:`~._revert_method`.

        Example::

            def do_write(self, values):
                # do stuff, and call the original method
                return do_write.origin(self, values)

            # patch method write of model
            model._patch_method('write', do_write)

            # this will call do_write
            records = model.search([...])
            records.write(...)

            # restore the original method
            model._revert_method('write')
        """
        cls = type(model_obj)
        origin = getattr(cls, name)
        method.origin = origin
        # propagate decorators from origin to method, and apply api decorator
        wrapped = api.propagate(origin, method)
        wrapped.origin = origin
        setattr(cls, name, wrapped)

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
            def wrapper(self, name):
                raise UserError(
                    _(
                        "Can't create %(model)s with name %(name)s quickly.\n"
                        "Please contact your system administrator to disable "
                        "this behaviour."
                    )
                    % {"model": self._name, "name": name}
                )

            return wrapper

        method_name = "name_create"
        for model in self:
            model_obj = self.env.get(model.model)
            if model.avoid_quick_create and model_obj is not None:
                # _wrap_name_create().origin = getattr(model_obj, method_name)
                # setattr(model_obj, method_name, _wrap_name_create())
                self._patch_method(model_obj, method_name, _wrap_name_create())
            else:
                method = getattr(model_obj, method_name, None)
                if method and hasattr(method, "origin"):
                    self._revert_method(model_obj, method_name)
        return True

    def _register_hook(self):
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
            self.pool.signal_changes()
        return res
