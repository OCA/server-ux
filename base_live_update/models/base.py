# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


import operator

from odoo import api, models, tools


class Base(models.AbstractModel):
    _inherit = "base"

    @tools.ormcache()
    def _live_update_active(self):
        return bool(
            self.env["live.update.notification"]
            .sudo()
            .search_count([("model_id.model", "=", self._name)])
        )

    def _write(self, vals):
        result = super()._write(vals)
        if self._live_update_active():
            self._live_update("write", dict(vals, __ids=self.ids))
        return result

    @api.model
    def _create(self, data_list):
        result = super()._create(data_list)
        if self._live_update_active():
            self._live_update(
                "create",
                list(
                    zip(
                        result.ids,
                        map(dict, map(operator.itemgetter("stored"), data_list)),
                    )
                ),
            )
        return result

    def unlink(self):
        result = super().unlink()
        if self._live_update_active():
            self._live_update("unlink", list(self.ids))
        return result

    def _live_update(self, action, data):
        @self.env.cr.precommit.add
        def __live_update():
            self._live_update_notify(
                action,
                data,
            )

    def _live_update_notify(self, action, data):
        self.env["bus.bus"]._sendone(
            "live.update.%s" % self._name,
            "live.update",
            dict(model=self._name, action=action, data=data),
        )
