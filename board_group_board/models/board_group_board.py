# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import api, fields, models


class BoardGroupBoard(models.Model):
    _name = "board.group.board"
    _order = "sequence"
    _description = "Board definition for group"

    sequence = fields.Integer()
    arch = fields.Text("Board definition", required=True)
    group_ids = fields.Many2many("res.groups", required=True)

    @api.constrains("arch")
    def _check_arch(self):
        """Be sure arch is syntactically correct"""
        preprocessing = self.env["board.board"]._arch_preprocessing
        for this in self:
            preprocessing(this.arch)

    def action_impose_all_users(self):
        """Impose board on all users"""
        for this in self:
            for user in self.env["res.users"].search([]):
                user._update_board_from_groups(this)

    def name_get(self):
        """Show groups as name"""
        return [(this.id, ", ".join(this.mapped("group_ids.name"))) for this in self]
