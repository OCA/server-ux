# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import api, models


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model_create_multi
    def create(self, vals_list):
        """Impose group board on new users"""
        result = super().create(vals_list)
        result._update_board_from_groups()
        return result

    def write(self, vals):
        """Impose group board if group changes"""
        result = super().write(vals)
        if "groups_id" in vals:
            self._update_board_from_groups()
        return result

    def _update_board_from_groups(self, group_board=None):
        """Create a custom view for current user based on group board definition"""
        board_action = self.env.ref("board.open_board_my_dash_action")
        board_view_id = board_action.views[0][0]
        for this in self:
            board = self.env["board.group.board"].search(
                [
                    ("group_ids", "in", this.groups_id.ids),
                ],
                limit=1,
            )
            if not board or group_board and group_board != board:
                continue
            self.env["ir.ui.view.custom"].sudo().create(
                {
                    "ref_id": board_view_id,
                    "user_id": this.id,
                    "arch": board.arch,
                }
            )
