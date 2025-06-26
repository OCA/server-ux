# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AnnouncementTag(models.Model):
    _name = "announcement.tag"
    _description = "Announcement Tags"

    name = fields.Char(required=True, translate=True)
    color = fields.Integer()
    parent_id = fields.Many2one(
        comodel_name="announcement.tag",
        string="Parent Tag",
        index=True,
        ondelete="cascade",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        index=True,
        help="Company related to this tag",
    )

    _sql_constraints = [("name_uniq", "unique (name)", "Tag name already exists!")]

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_("You cannot create recursive tags."))

    @api.depends("parent_id", "name")
    def _compute_display_name(self):
        for item in self:
            item.display_name = (
                f"{item.parent_id.name} / {item.name}" if item.parent_id else item.name
            )
