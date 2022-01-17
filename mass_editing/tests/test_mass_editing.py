# Copyright 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# Copyright 2018 Aitor Bouzas <aitor.bouzas@adaptivecity.com)
# Copyrithg 2020 Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ast import literal_eval

from odoo.exceptions import ValidationError
from odoo.tests import Form, common


@common.tagged("-at_install", "post_install")
class TestMassEditing(common.SavepointCase):
    def setUp(self):
        super().setUp()

        self.MassEditingWizard = self.env["mass.editing.wizard"]
        self.ResPartnerTitle = self.env["res.partner.title"]
        self.ResLang = self.env["res.lang"]
        self.IrTranslation = self.env["ir.translation"]
        self.IrActionsActWindow = self.env["ir.actions.act_window"]

        self.mass_editing_user = self.env.ref("mass_editing.mass_editing_user")
        self.mass_editing_partner = self.env.ref("mass_editing.mass_editing_partner")
        self.mass_editing_partner_title = self.env.ref(
            "mass_editing.mass_editing_partner_title"
        )

        self.users = self.env["res.users"].search([])
        self.user = self.env.ref("base.user_demo")
        self.partner = self.user.partner_id
        self.partner_title = self._create_partner_title()

    def _create_partner_title(self):
        """Create a Partner Title."""
        # Loads German to work with translations
        self.ResLang._activate_lang("de_DE")
        # Creating the title in English
        partner_title = self.ResPartnerTitle.create(
            {"name": "Ambassador", "shortcut": "Amb."}
        )
        # Adding translated terms
        ctx = {"lang": "de_DE"}
        partner_title.with_context(ctx).write(
            {"name": "Botschafter", "shortcut": "Bots."}
        )
        return partner_title

    def _create_wizard_and_apply_values(self, server_action, items, vals):
        action = server_action.with_context(
            active_model=items._name,
            active_ids=items.ids,
        ).run()
        wizard = (
            self.env[action["res_model"]]
            .with_context(
                literal_eval(action["context"]),
            )
            .create(vals)
        )
        wizard.button_apply()
        return wizard

    def test_wiz_fields_view_get(self):
        """Test whether fields_view_get method returns arch.
        with dynamic fields.
        """
        result = self.MassEditingWizard.with_context(
            server_action_id=self.mass_editing_user.id,
            active_ids=[],
        ).fields_view_get()
        arch = result.get("arch", "")
        self.assertTrue(
            "selection__email" in arch,
            "Fields view get must return architecture with fields" "created dynamicaly",
        )

    def test_wiz_read_fields(self):
        """Test whether read method returns all fields or not."""
        fields_view = self.MassEditingWizard.with_context(
            server_action_id=self.mass_editing_user.id,
            active_ids=[],
        ).fields_view_get()
        fields = list(fields_view["fields"].keys())
        # add a real field
        fields.append("display_name")
        vals = {"selection__email": "remove", "selection__phone": "remove"}
        mass_wizard = self._create_wizard_and_apply_values(
            self.mass_editing_user, self.users, vals
        )
        result = mass_wizard.read(fields)[0]
        self.assertTrue(
            all([field in result for field in fields]), "Read must return all fields."
        )

    def test_mass_edit_partner_title(self):
        """Test Case for MASS EDITING which will check if translation
        was loaded for new partner title, and if they are removed
        as well as the value for the abbreviation for the partner title."""
        search_domain = [
            ("res_id", "=", self.partner_title.id),
            ("type", "=", "model"),
            ("name", "=", "res.partner.title,shortcut"),
            ("lang", "=", "de_DE"),
        ]
        translation_ids = self.IrTranslation.search(search_domain)
        self.assertEqual(
            len(translation_ids),
            1,
            "Translation for Partner Title's Abbreviation " "was not loaded properly.",
        )
        # Removing partner title with mass edit action
        vals = {"selection__shortcut": "remove"}
        self._create_wizard_and_apply_values(
            self.mass_editing_partner_title, self.partner_title, vals
        )
        self.assertEqual(
            self.partner_title.shortcut,
            False,
            "Partner Title's Abbreviation should be removed.",
        )
        # Checking if translations were also removed
        translation_ids = self.IrTranslation.search(search_domain)
        self.assertEqual(
            len(translation_ids),
            0,
            "Translation for Partner Title's Abbreviation " "was not removed properly.",
        )

    def test_mass_edit_email(self):
        """Test Case for MASS EDITING which will remove and after add
        User's email and will assert the same."""
        # Remove email and phone
        vals = {"selection__email": "remove", "selection__phone": "remove"}
        self._create_wizard_and_apply_values(self.mass_editing_user, self.user, vals)
        self.assertEqual(self.user.email, False, "User's Email should be removed.")
        # Set email address
        vals = {"selection__email": "set", "email": "sample@mycompany.com"}
        self._create_wizard_and_apply_values(self.mass_editing_user, self.user, vals)
        self.assertNotEqual(self.user.email, False, "User's Email should be set.")

    def test_mass_edit_m2m_categ(self):
        """Test Case for MASS EDITING which will remove and add
        Partner's category m2m."""
        # Remove m2m categories
        vals = {"selection__category_id": "remove_m2m"}
        self._create_wizard_and_apply_values(self.mass_editing_user, self.user, vals)
        self.assertNotEqual(
            self.user.category_id, False, "User's category should be removed."
        )
        # Add m2m categories
        dist_categ_id = self.env.ref("base.res_partner_category_14").id
        vend_categ_id = self.env.ref("base.res_partner_category_0").id
        vals = {
            "selection__category_id": "add",
            "category_id": [[6, 0, [dist_categ_id, vend_categ_id]]],
        }
        self._create_wizard_and_apply_values(self.mass_editing_user, self.user, vals)
        self.assertTrue(
            all(
                item in self.user.category_id.ids
                for item in [dist_categ_id, vend_categ_id]
            ),
            "Partner's category should be added.",
        )
        # Remove one m2m category
        vals = {
            "selection__category_id": "remove_m2m",
            "category_id": [[6, 0, [vend_categ_id]]],
        }
        self._create_wizard_and_apply_values(self.mass_editing_user, self.user, vals)
        self.assertTrue(
            [dist_categ_id] == self.user.category_id.ids,
            "User's category should be removed.",
        )

    def test_check_field_model_constraint(self):
        """Test that it's not possible to create inconsistent mass edit actions"""
        with self.assertRaises(ValidationError):
            self.mass_editing_user.write(
                {"model_id": self.env.ref("base.model_res_country").id}
            )

    def test_mass_edit_o2m_child_ids(self):
        """Test Case for MASS EDITING which will remove and after add
        Partner's child_ids and will assert the same."""
        # Add one child_ids
        self.env["res.partner"].with_user(self.user).create(
            {"name": "test", "parent_id": self.partner.id}
        )
        self.assertTrue(self.partner.child_ids)
        # Remove one child_ids
        vals = {"selection__child_ids": "remove_o2m"}
        self._create_wizard_and_apply_values(
            self.mass_editing_partner, self.partner, vals
        )
        self.assertFalse(
            self.partner.child_ids.exists(), "Partner's child_ids should be removed."
        )
        # Set one child_ids
        vals = {
            "selection__child_ids": "set_o2m",
            "child_ids": [(0, 0, {"name": "test", "parent_id": self.partner.id})],
        }
        self._create_wizard_and_apply_values(
            self.mass_editing_partner, self.partner, vals
        )
        self.assertTrue(self.partner.child_ids, "Partner's log_ids should be set.")

    def test_onchanges(self):
        """Test that form onchanges do what they're supposed to"""
        # Test change on server_action.model_id : clear mass_edit_line_ids
        server_action_form = Form(self.mass_editing_user)
        self.assertGreater(
            len(server_action_form.mass_edit_line_ids),
            0,
            "Mass Editing User demo data should have lines",
        )
        server_action_form.model_id = self.env.ref("base.model_res_country")
        self.assertEqual(
            len(server_action_form.mass_edit_line_ids),
            0,
            "Mass edit lines should be removed when changing model",
        )
        # Test change on mass_edit_line field_id : set widget_option
        mass_edit_line_form = Form(
            self.env.ref("mass_editing.mass_editing_user_line_1")
        )
        mass_edit_line_form.field_id = self.env.ref(
            "base.field_res_partner__category_id"
        )
        self.assertEqual(mass_edit_line_form.widget_option, "many2many_tags")
        mass_edit_line_form.field_id = self.env.ref(
            "base.field_res_partner__image_1920"
        )
        self.assertEqual(mass_edit_line_form.widget_option, "image")
        mass_edit_line_form.field_id = self.env.ref("base.field_res_users__country_id")
        self.assertFalse(mass_edit_line_form.widget_option)
