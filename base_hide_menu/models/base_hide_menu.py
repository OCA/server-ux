# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BaseHideMenu(models.Model):
    _name = "base.hide.menu"
    _description = "Base Hide Menu"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    parent_menu_id = fields.Many2one(
        "ir.ui.menu", "Parent Menu", domain="[('parent_id', '!=', False)]"
    )
    menu_item_ids = fields.Many2many(
        'base.hide.menu.item', 'hide_menu_item_rel',
        'hide_menu_id', 'record_id', string='Sub-Menus',
        compute="_compute_menu_items_ids", store=True
    )
    all_hidden = fields.Boolean(compute='_compute_all_hidden')

    def _compute_all_hidden(self):
        for rec in self:
            rec.all_hidden = False
            if all(not menu.active for menu in
                   rec.mapped('menu_item_ids.menu_id')):
                rec.all_hidden = True

    def button_hide_all(self):
        self.ensure_one()
        self.menu_item_ids.hide_menu()

    def _get_forbidden_menu_ids(self):
        return self.env["ir.ui.menu"].search(
            [("name", "=like", "Hidden Menus")]).ids

    def _prepare_hide_menu_item_vals(self, menu_id):
        return {
            "menu_id": menu_id.id,
            "complete_name": menu_id.complete_name,
            "visible": menu_id.active
        }

    @api.depends("parent_menu_id")
    def _compute_menu_items_ids(self):
        for rec in self:
            rec.menu_item_ids = []
            menu_item_ids = []
            forbidden_menu_ids = rec._get_forbidden_menu_ids()
            if rec.parent_menu_id:
                if rec.parent_menu_id.id in forbidden_menu_ids:
                    raise ValidationError(_(
                        "Invalid selected parent menu, you cannot hide this menu."
                    ))
                menu_ids = rec.parent_menu_id.child_id
                for menu_id in menu_ids:
                    vals = rec._prepare_hide_menu_item_vals(menu_id)
                    menu_item_ids.append(
                        self.env["base.hide.menu.item"].create(vals).id)
                rec.menu_item_ids = [(6, 0, menu_item_ids)]


class BaseHideMenuItem(models.Model):
    _name = "base.hide.menu.item"
    _description = "Base Hide Menu Item"

    menu_id = fields.Many2one(
        "ir.ui.menu", "Sub-Menu", required=True, readonly=True)
    complete_name = fields.Char(readonly=True)
    visible = fields.Boolean(readonly=True)

    def hide_menu(self):
        for record in self:
            menu_id = record.menu_id
            if menu_id.active:
                menu_id.active = False
                record.visible = False

    def unhide_menu(self):
        for record in self:
            menu_id = record.menu_id
            if not menu_id.active:
                menu_id.active = True
                record.visible = True
