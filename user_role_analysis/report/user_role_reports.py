# Copyright 2021 ForgeFlow, S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models
from odoo.tools import sql


class UserModelPermissionReport(models.Model):
    _name = "user.model.permission.report"
    _auto = False
    _description = "User Model Permission Report"
    _order = "x_user_id, x_group_name, x_model_name, id"

    x_user_id = fields.Many2one(comodel_name="res.users", string="User", readonly=True)
    x_group_name = fields.Char(string="Group", readonly=True)
    x_model_name = fields.Char(string="Model", readonly=True)
    x_read = fields.Boolean(string="Read", readonly=True)
    x_write = fields.Boolean(string="Write", readonly=True)
    x_create = fields.Boolean(string="Create", readonly=True)
    x_unlink = fields.Boolean(string="Unlink", readonly=True)

    def init(self):
        sql.drop_view_if_exists(self.env.cr, self._table)
        self._cr.execute(
            """
    CREATE OR REPLACE VIEW user_model_permission_report AS (
        SELECT
            ROW_NUMBER() OVER () as id,
            ru.id as x_user_id,
            rg.name as x_group_name,
            im.name as x_model_name,
            bool_or(ima.perm_read) as x_read,
            bool_or(ima.perm_write) as x_write,
            bool_or(ima.perm_create) as x_create,
            bool_or(ima.perm_unlink) as x_unlink
        FROM res_users ru
        JOIN res_groups_users_rel rel1 ON rel1.uid = ru.id
        LEFT JOIN res_groups_implied_rel rel2 ON rel2.gid = rel1.gid
        LEFT JOIN res_groups rg ON (rel1.gid = rg.id OR rel2.hid = rg.id)
        JOIN ir_model_access ima ON ima.group_id = rg.id
        JOIN ir_model im ON ima.model_id = im.id
        WHERE ima.active
        GROUP BY ru.id, im.model, im.name, rg.name
        ORDER BY ru.id, rg.name, im.name
    )"""
        )


class UserMenuPermissionReport(models.Model):
    _name = "user.menu.permission.report"
    _auto = False
    _description = "User Menu Permission Report"
    _order = "x_user_id, x_group_name, x_menu_complete_name, id"

    x_user_id = fields.Many2one(comodel_name="res.users", string="User", readonly=True)
    x_group_name = fields.Char(string="Group", readonly=True)
    x_menu_complete_name = fields.Char(string="Menu", readonly=True)

    def init(self):
        sql.drop_view_if_exists(self.env.cr, self._table)
        self._cr.execute(
            """
    CREATE OR REPLACE VIEW user_menu_permission_report AS (
        WITH sub AS (
            SELECT
                ru.id,
                rg.name,
                ium.id as ium_id
            FROM res_users ru
            JOIN res_groups_users_rel rel1 ON rel1.uid = ru.id
            LEFT JOIN res_groups_implied_rel rel2 ON rel2.gid = rel1.gid
            LEFT JOIN res_groups rg ON (rel1.gid = rg.id OR rel2.hid = rg.id)
            JOIN ir_ui_menu_group_rel mgr ON mgr.gid = rg.id
            JOIN ir_ui_menu ium ON ium.id = mgr.menu_id
            WHERE ium.active
            GROUP BY ru.id, rg.name, ium.id
        )
        SELECT
            ROW_NUMBER() OVER () as id,
            sub.id as x_user_id,
            sub.name as x_group_name,
            trim(leading '.../' from COALESCE(ium7.name, '...') || '/'
                || COALESCE(ium6.name, '...') || '/' || COALESCE(ium5.name, '...')
                || '/' || COALESCE(ium4.name, '...') || '/' ||
                COALESCE(ium3.name, '...') || '/' || COALESCE(ium2.name, '...') ||
                '/' || ium.name) as x_menu_complete_name
        FROM sub
        JOIN ir_ui_menu ium ON ium.id = sub.ium_id
        LEFT JOIN ir_ui_menu ium2 ON (
            ium.parent_id = ium2.id AND ium2.active AND ium2.id IN (
                SELECT ium_id FROM sub))
        LEFT JOIN ir_ui_menu ium3 ON (
            ium2.parent_id = ium3.id AND ium3.active AND ium3.id IN (
                SELECT ium_id FROM sub))
        LEFT JOIN ir_ui_menu ium4 ON (
            ium3.parent_id = ium4.id AND ium4.active AND ium4.id IN (
                SELECT ium_id FROM sub))
        LEFT JOIN ir_ui_menu ium5 ON (
            ium4.parent_id = ium5.id AND ium5.active AND ium5.id IN (
                SELECT ium_id FROM sub))
        LEFT JOIN ir_ui_menu ium6 ON (
            ium5.parent_id = ium6.id AND ium6.active AND ium6.id IN (
                SELECT ium_id FROM sub))
        LEFT JOIN ir_ui_menu ium7 ON (
            ium6.parent_id = ium7.id AND ium7.active AND ium7.id IN (
                SELECT ium_id FROM sub))
        ORDER BY sub.id, sub.name, x_menu_complete_name
    )"""
        )


class RoleModelPermissionReport(models.Model):
    _name = "role.model.permission.report"
    _auto = False
    _description = "Role Model Permission Report"
    _order = "x_role_id, x_model_name, id"

    x_role_id = fields.Many2one(
        comodel_name="res.users.role", string="Role", readonly=True
    )
    x_model_name = fields.Char(string="Model", readonly=True)
    x_read = fields.Boolean(string="Read", readonly=True)
    x_write = fields.Boolean(string="Write", readonly=True)
    x_create = fields.Boolean(string="Create", readonly=True)
    x_unlink = fields.Boolean(string="Unlink", readonly=True)

    def init(self):
        sql.drop_view_if_exists(self.env.cr, self._table)
        self._cr.execute(
            """
    CREATE OR REPLACE VIEW role_model_permission_report AS (
        SELECT
            ROW_NUMBER() OVER () as id,
            rur.id as x_role_id,
            im.name as x_model_name,
            bool_or(ima.perm_read) as x_read,
            bool_or(ima.perm_write) as x_write,
            bool_or(ima.perm_create) as x_create,
            bool_or(ima.perm_unlink) as x_unlink
        FROM res_users_role rur
        LEFT JOIN res_groups_implied_rel rel ON rel.gid = rur.group_id
        LEFT JOIN res_groups rg ON (rur.group_id = rg.id OR rel.hid = rg.id)
        JOIN ir_model_access ima ON ima.group_id = rg.id
        JOIN ir_model im ON ima.model_id = im.id
        WHERE ima.active
        GROUP BY rur.id, im.name
        ORDER BY rur.id, im.name
    )"""
        )


class RoleMenuPermissionReport(models.Model):
    _name = "role.menu.permission.report"
    _auto = False
    _description = "Role Menu Permission Report"
    _order = "x_role_id, x_group_name, x_menu_complete_name, id"

    x_role_id = fields.Many2one(
        comodel_name="res.users.role", string="Role", readonly=True
    )
    x_group_name = fields.Char(string="Group", readonly=True)
    x_menu_complete_name = fields.Char(string="Menu", readonly=True)

    def init(self):
        sql.drop_view_if_exists(self.env.cr, self._table)
        self._cr.execute(
            """
    CREATE OR REPLACE VIEW role_menu_permission_report AS (
        WITH sub AS (
            SELECT
                rur.id,
                rg.name,
                ium.id as ium_id
            FROM res_users_role rur
            LEFT JOIN res_groups_implied_rel rel ON rel.gid = rur.group_id
            LEFT JOIN res_groups rg ON (rur.group_id = rg.id OR rel.hid = rg.id)
            JOIN ir_ui_menu_group_rel mgr ON mgr.gid = rg.id
            JOIN ir_ui_menu ium ON ium.id = mgr.menu_id
            WHERE ium.active
            GROUP BY rur.id, rg.name, ium.id
        )
        SELECT
            ROW_NUMBER() OVER () as id,
            sub.id as x_role_id,
            sub.name as x_group_name,
            trim(leading '.../' from COALESCE(ium7.name, '...') || '/'
                || COALESCE(ium6.name, '...') || '/' || COALESCE(ium5.name, '...')
                || '/' || COALESCE(ium4.name, '...') || '/' ||
                COALESCE(ium3.name, '...') || '/' || COALESCE(ium2.name, '...') ||
                '/' || ium.name) as x_menu_complete_name
        FROM sub
        JOIN ir_ui_menu ium ON ium.id = sub.ium_id
        LEFT JOIN ir_ui_menu ium2 ON (
            ium.parent_id = ium2.id AND ium2.active AND ium2.id IN (
                SELECT ium_id FROM sub))
        LEFT JOIN ir_ui_menu ium3 ON (
            ium2.parent_id = ium3.id AND ium3.active AND ium3.id IN (
                SELECT ium_id FROM sub))
        LEFT JOIN ir_ui_menu ium4 ON (
            ium3.parent_id = ium4.id AND ium4.active AND ium4.id IN (
                SELECT ium_id FROM sub))
        LEFT JOIN ir_ui_menu ium5 ON (
            ium4.parent_id = ium5.id AND ium5.active AND ium5.id IN (
                SELECT ium_id FROM sub))
        LEFT JOIN ir_ui_menu ium6 ON (
            ium5.parent_id = ium6.id AND ium6.active AND ium6.id IN (
                SELECT ium_id FROM sub))
        LEFT JOIN ir_ui_menu ium7 ON (
            ium6.parent_id = ium7.id AND ium7.active AND ium7.id IN (
                SELECT ium_id FROM sub))
        ORDER BY sub.id, sub.name, x_menu_complete_name
    )"""
        )
