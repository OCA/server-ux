# © 2016 Opener B.V. (<https://opener.am>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command, api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    technical_features = fields.Boolean(
        compute="_compute_technical_features",
        inverse="_inverse_technical_features",
        help="Whether the user has technical features always enabled.",
    )

    def has_group(self, group_ext_id: str) -> bool:
        # OVERRIDE to forcefully enable debug mode through context key
        self.ensure_one()
        if (
            group_ext_id == "base.group_no_one"
            and self.env.context.get("force_debug_mode")
            and self.technical_features
        ):
            return True
        return super().has_group(group_ext_id)

    @api.depends("group_ids")
    def _compute_technical_features(self):
        for user in self:
            user.technical_features = user.has_group(
                "base_technical_features.group_technical_features"
            )

    def _inverse_technical_features(self):
        """Map boolean field value to group membership"""
        group = self.env.ref("base_technical_features.group_technical_features")
        if to_add := self.filtered("technical_features"):
            to_add.sudo().write({"group_ids": [Command.link(group.id)]})
        if to_remove := self - to_add:
            to_remove.sudo().write({"group_ids": [Command.unlink(group.id)]})

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ["technical_features"]

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + ["technical_features"]
