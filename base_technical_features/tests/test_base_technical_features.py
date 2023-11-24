from lxml import etree

from odoo.exceptions import AccessError
from odoo.tests import common


class TestBaseTechnicalFeatures(common.TransactionCase):
    def test_01_visible_menus(self):
        """ A technical feature is visible to the user with the technical \
        features group """
        menu_obj = self.env["ir.ui.menu"].with_context(**{"ir.ui.menu.full_list": True})
        menu_id = menu_obj.search(
            [("groups_id", "=", self.env.ref("base.group_no_one").id)], limit=1
        ).id
        self.env.user.write({"technical_features": False})
        self.env.user._compute_show_technical_features()
        self.assertNotIn(menu_id, menu_obj._visible_menu_ids())
        self.env.user.write({"technical_features": True})
        self.env.user._compute_show_technical_features()
        self.assertIn(menu_id, menu_obj._visible_menu_ids())

    def test02_visible_fields(self):
        """ A technical field is visible when its form is loaded by a user \
        with the technical features group """

        def get_partner_field():
            xml = etree.fromstring(
                self.env["res.users"]
                .get_view(view_id=self.env.ref("base.view_users_form").id)["arch"]
                .encode("utf-8")
            )
            return xml.xpath('//div/group/field[@name="partner_id"]')

        self.env.user.write({"technical_features": False})
        self.assertEqual(len(get_partner_field()), 0)
        self.env.user.write({"technical_features": True})
        self.assertEqual(len(get_partner_field()), 1)

    def test03_user_access(self):
        """ Setting the user pref raises an access error if the user is not \
        in group_no_one """
        user = self.env["res.users"].create(
            {
                "name": "Test user technical features",
                "login": "testusertechnicalfeatures",
                "groups_id": [(6, 0, [])],
            }
        )
        self.env.user._compute_show_technical_features()
        self.env.user._compute_technical_features()
        with self.assertRaises(AccessError):
            self.env["res.users"].browse(user.id).sudo().write(
                {"technical_features": True}
            )
        with self.assertRaises(AccessError):
            user.write({"technical_features": True})
        user.write({"groups_id": [(4, self.env.ref("base.group_no_one").id)]})
        self.env["res.users"].browse(user.id).sudo().write({"technical_features": True})
