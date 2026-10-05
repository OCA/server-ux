# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.tests import TransactionCase, new_test_user


class TestForwardReviewer(TransactionCase):
    def test_next_reviewer_is_an_internal_user(self):
        """Portal users cannot act on reviews, so a review is not forwarded
        to them."""
        portal = self.env["res.users"].create(
            {
                "name": "Portal",
                "login": "portal_reviewer",
                "groups_id": [Command.set(self.env.ref("base.group_portal").ids)],
            }
        )
        internal = new_test_user(self.env, login="internal_reviewer")
        domain = (
            self.env["tier.validation.forward.wizard"]
            ._fields["forward_reviewer_id"]
            .domain
        )
        self.assertFalse(portal.filtered_domain(domain))
        self.assertTrue(internal.filtered_domain(domain))
