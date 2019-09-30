# Copyright 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# Copyright 2018 Aitor Bouzas <aitor.bouzas@adaptivecity.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# import ast

from odoo.modules import registry
from odoo.tests import common

from ..hooks import uninstall_hook


class TestMassEditing(common.SavepointCase):
    at_install = False
    post_install = True

    def setUp(self):
        super().setUp()

        self.MassEditingWizard = self.env["mass.editing.wizard"]
        self.ResPartnerTitle = self.env["res.partner.title"]
        self.ResLang = self.env["res.lang"]
        self.IrTranslation = self.env["ir.translation"]
        self.IrActionsActWindow = self.env["ir.actions.act_window"]

        self.mass_editing_user = self.env.ref("mass_editing.mass_editing_user")
        self.mass_editing_partner_title = self.env.ref(
            "mass_editing.mass_editing_partner_title"
        )

        self.users = self.env["res.users"].search([])
        self.user = self.env.ref("base.user_demo")
        self.partner_title = self._create_partner_title()

    def _create_partner_title(self):
        """Create a Partner Title."""
        # Loads German to work with translations
        self.ResLang.load_lang("de_DE")
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

    def _create_wizard_and_apply_values(self, mass_editing, items, vals):
        return self.MassEditingWizard.with_context(
            mass_operation_mixin_name="mass.editing",
            mass_operation_mixin_id=mass_editing.id,
            active_ids=items.ids,
        ).create(vals)

    def test_wiz_fields_view_get(self):
        """Test whether fields_view_get method returns arch.
        with dynamic fields.
        """
        result = self.MassEditingWizard.with_context(
            mass_operation_mixin_name="mass.editing",
            mass_operation_mixin_id=self.mass_editing_user.id,
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
            mass_operation_mixin_name="mass.editing",
            mass_operation_mixin_id=self.mass_editing_user.id,
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

    def test_sidebar_action(self):
        """Test if Sidebar Action is added / removed to / from give object."""

        self.assertTrue(
            self.mass_editing_user.ref_ir_act_window_id, "Sidebar action must exist."
        )

        # Remove the sidebar actions
        self.mass_editing_user.disable_mass_operation()
        self.assertFalse(
            self.mass_editing_user.ref_ir_act_window_id,
            "Sidebar action must be removed.",
        )

    def test_unlink_mass(self):
        """Test if related actions are removed when mass editing
        record is unlinked."""
        act_window = self.mass_editing_user.ref_ir_act_window_id

        self.mass_editing_user.unlink()

        self.assertFalse(
            act_window.exists(),
            "Sidebar action must be removed when mass" " editing is unlinked.",
        )

    def test_uninstall_hook(self):
        """Test if related actions are removed when mass editing
        record is uninstalled."""
        uninstall_hook(self.cr, registry)
        mass_action_id = self.mass_editing_user.ref_ir_act_window_id.id
        count = len(self.IrActionsActWindow.browse(mass_action_id))
        self.assertTrue(
            count == 0,
            "Sidebar action must be removed when mass"
            " editing module is uninstalled.",
        )
