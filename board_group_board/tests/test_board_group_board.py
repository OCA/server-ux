# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo.tests.common import TransactionCase


class TestBoardGroupBoard(TransactionCase):
    def test_all(self):
        user_admin = self.env.ref("base.user_admin")
        user_demo = self.env.ref("base.user_demo")
        admin_board = self.env.ref("board_group_board.board_admin")
        all_board = self.env.ref("board_group_board.board_all")
        (admin_board + all_board).action_impose_all_users()
        self.assertEqual(
            self._get_board_arch(user_admin),
            admin_board.arch,
        )
        self.assertEqual(
            self._get_board_arch(user_demo),
            all_board.arch,
        )
        user_new = self.env["res.users"].create(
            {
                "name": "Testuser",
                "login": "board_group_board@oca.org",
            }
        )
        self.assertEqual(
            self._get_board_arch(user_new),
            all_board.arch,
        )
        user_new.groups_id += self.env.ref("base.group_erp_manager")
        self.assertEqual(
            self._get_board_arch(user_new),
            admin_board.arch,
        )

    def _get_board_arch(self, user):
        board_action = self.env.ref("board.open_board_my_dash_action")
        board_view_id = board_action.views[0][0]
        return (
            self.env["ir.ui.view.custom"]
            .search(
                [("user_id", "=", user.id), ("ref_id", "=", board_view_id)], limit=1
            )
            .arch
        )
