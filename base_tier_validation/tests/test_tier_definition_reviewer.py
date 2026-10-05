# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.tests import TransactionCase, new_test_user


class TestTierDefinitionReviewer(TransactionCase):
    def test_reviewer_is_an_internal_user(self):
        """Portal users cannot act on reviews, so they are not offered as the
        reviewer of a tier definition."""
        portal = self.env["res.users"].create(
            {
                "name": "Portal",
                "login": "portal_reviewer",
                "groups_id": [Command.set(self.env.ref("base.group_portal").ids)],
            }
        )
        internal = new_test_user(self.env, login="internal_reviewer")
        domain = self.env["tier.definition"]._fields["reviewer_id"].domain
        self.assertFalse(portal.filtered_domain(domain))
        self.assertTrue(internal.filtered_domain(domain))
