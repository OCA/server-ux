# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import models


class Base(models.AbstractModel):
    _inherit = "base"

    def _should_hide_action(self, allowed_group_ids):
        if not allowed_group_ids:
            return False
        user_groups = self.env.user.groups_id
        user_has_permission = bool(allowed_group_ids & user_groups)
        return not user_has_permission

    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        result = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        ir_model = (
            self.env["ir.model"].sudo().search([("model", "=", self._name)], limit=1)
        )
        if view_type not in ("form", "tree", "kanban") or not ir_model:
            return result
        hide_duplicate = self._should_hide_action(ir_model.duplicate_allowed_group_ids)
        hide_delete = self._should_hide_action(ir_model.delete_allowed_group_ids)
        if not hide_duplicate and not hide_delete:
            return result
        arch = etree.fromstring(result["arch"])
        if view_type == "form" and hide_duplicate:
            arch.set("duplicate", "0")
        if hide_delete:
            arch.set("delete", "0")
        result["arch"] = etree.tostring(arch, encoding="unicode")
        return result
