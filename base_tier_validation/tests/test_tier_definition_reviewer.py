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

    def test_reviewer_group_is_internal(self):
        """The portal and public roles, and groups implying them, are not
        offered as reviewer group."""
        portal = self.env.ref("base.group_portal")
        public = self.env.ref("base.group_public")
        portal_based = self.env["res.groups"].create(
            {"name": "Portal based", "implied_ids": [Command.link(portal.id)]}
        )
        internal = self.env["res.groups"].create({"name": "Reviewers"})
        domain = (
            self.env["tier.definition"]
            ._fields["reviewer_group_id"]
            .domain(self.env["tier.definition"])
        )
        allowed = self.env["res.groups"].search(domain)
        self.assertFalse((portal | public | portal_based) & allowed)
        self.assertIn(internal, allowed)
