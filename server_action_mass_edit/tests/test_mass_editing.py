# Copyright 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# Copyright 2018 Aitor Bouzas <aitor.bouzas@adaptivecity.com)
# Copyrithg 2020 Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ast import literal_eval

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import Form, common, new_test_user

from odoo.addons.base.models.ir_actions import IrActionsServer


def fake_onchange_model_id(self):
    result = {
        "warning": {
            "title": "This is a fake onchange",
        },
    }
    return result


@common.tagged("-at_install", "post_install")
class TestMassEditing(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.MassEditingWizard = cls.env["mass.editing.wizard"]
        cls.ResCountryGroup = cls.env["res.country.group"]
        cls.ResLang = cls.env["res.lang"]
        cls.ServerAction = cls.env["ir.actions.server"]
        cls.IrActionsActWindow = cls.env["ir.actions.act_window"]

        user_model = cls.env.ref("base.model_res_users")
        cls.mass_editing_user = cls._create_mass_editing_user_server_action(user_model)

        partner_model = cls.env.ref("base.model_res_partner")
        cls.mass_editing_partner = cls._create_mass_editing_user_server_action(
            partner_model
        )

        cls.mass_editing_company = cls._create_mass_editing_company_server_action()

        cls.mass_editing_country_group = (
            cls._create_mass_editing_country_group_server_action()
        )
        user_admin = cls.env.ref("base.user_admin")
        cls.users = cls.env["res.users"].search([("id", "not in", (user_admin.id))])
        cls.user = new_test_user(
            cls.env,
            login="test-mass_editing-user",
            groups="base.group_system",
        )
        cls.country_group = cls._create_country_group()

    @classmethod
    def _create_mass_editing_user_server_action(cls, model_id):
        """Create a Mass Editing Server Action for Users Object."""
        fields = [
            "email",
            "phone",
            "comment",
            "country_id",
            "is_company",
            "lang",
            "company_type",
            "image_1920",
            "bank_ids",
        ]
        model_name = model_id.model.replace(".", "_")
        server_action = cls.ServerAction.create(
            {
                "name": "Mass Edit",
                "model_id": model_id.id,
                "state": "mass_edit",
                "mass_edit_line_ids": [
                    Command.create(
                        {
                            "field_id": cls.env.ref(
                                "base.field_" + model_name + "__" + field
                            ).id
                        }
                    )
                    for field in fields
                ],
            }
        )
        server_action.create_action()
        return server_action

    @classmethod
    def _create_mass_editing_company_server_action(cls):
        """Create a Mass Editing Server Action for Company Object."""
        server_action = cls.ServerAction.create(
            {
                "name": "Mass Edit",
                "model_id": cls.env.ref("base.model_res_company").id,
                "state": "mass_edit",
                "mass_edit_line_ids": [
                    Command.create(
                        {
                            "field_id": cls.env.ref(
                                "base.field_res_company__currency_id"
                            ).id
                        }
                    ),
                    Command.create(
                        {
                            "field_id": cls.env.ref(
                                "base.field_res_company__child_ids"
                            ).id
                        }
                    ),
                ],
            }
        )
        server_action.create_action()
        return server_action

    @classmethod
    def _create_mass_editing_country_group_server_action(cls):
        """Create a Mass Editing Server Action for Country Group Object."""
        server_action = cls.ServerAction.create(
            {
                "name": "Mass Edit",
                "model_id": cls.env.ref("base.model_res_country_group").id,
                "state": "mass_edit",
                "mass_edit_line_ids": [
                    Command.create(
                        {
                            "field_id": cls.env.ref(
                                "base.field_res_country_group__name"
                            ).id
                        }
                    ),
                    Command.create(
                        {
                            "field_id": cls.env.ref(
                                "base.field_res_country_group__code"
                            ).id
                        }
                    ),
                ],
            }
        )
        server_action.create_action()
        return server_action

    @classmethod
    def _create_country_group(cls):
        """Create a Country Group Category."""
        # Loads German to work with translations
        cls.ResLang._activate_lang("de_DE")
        # Creating the Country Group in English
        country_group = cls.ResCountryGroup.create(
            {"name": "Commonwealth of Independent States", "code": "CIS"}
        )
        # Adding translated terms
        country_group.with_context(lang="de_DE").write(
            {"name": "Gemeinschaft Unabhängiger Staaten", "code": "GUS"}
        )
        return country_group

    def _create_wizard_and_apply_values(self, server_action, items, vals):
        action = server_action.with_context(
            active_model=items._name,
            active_ids=items.ids,
        ).run()
        wizard = (
            self.env[action["res_model"]]
            .with_context(
                **literal_eval(action["context"]),
            )
            .create(vals)
        )
        wizard.button_apply()
        return wizard

    def test_wzd_default_get(self):
        """Test whether `operation_description_danger` is correct"""
        wzd_obj = self.MassEditingWizard.with_context(
            server_action_id=self.mass_editing_user.id,
            active_ids=[1],
            original_active_ids=[1],
        )
        result = wzd_obj.default_get(
            fields=[],
        )
        self.assertEqual(
            result["operation_description_info"],
            "The treatment will be processed on the 1 selected record(s).",
        )
        self.assertFalse(
            result["operation_description_warning"],
        )
        self.assertFalse(
            result["operation_description_danger"],
        )

        result = wzd_obj.with_context(active_ids=[]).default_get(
            fields=[],
        )
        self.assertFalse(
            result["operation_description_info"],
        )
        self.assertEqual(
            result["operation_description_warning"],
            (
                "You have selected 1 record(s) that can not be processed.\n"
                "Only 0 record(s) will be processed."
            ),
        )
        self.assertFalse(
            result["operation_description_danger"],
        )

        result = wzd_obj.with_context(original_active_ids=[]).default_get(
            fields=[],
        )
        self.assertFalse(
            result["operation_description_info"],
        )
        self.assertFalse(
            result["operation_description_warning"],
        )
        self.assertEqual(
            result["operation_description_danger"],
            "None of the 1 record(s) you have selected can be processed.",
        )

    def test_wiz_fields_view_get(self):
        """Test whether fields_view_get method returns arch.
        with dynamic fields.
        """
        view_id = self.env.ref("server_action_mass_edit.view_mass_editing_wizard_form")
        view_id.mass_server_action_id = False
        result = self.MassEditingWizard.with_context(
            active_ids=[],
        ).get_view(view_id=view_id.id)
        arch = result.get("arch", "")
        self.assertTrue(
            "selection__email" not in arch,
            "Fields view get must return architecture w/o fields created dynamicaly",
        )
        view_id.mass_server_action_id = self.mass_editing_user
        result = self.MassEditingWizard.with_context(
            server_action_id=self.mass_editing_user.id,
            active_ids=[],
        ).get_view(view_id=view_id.id)
        arch = result.get("arch", "")
        self.assertTrue(
            "selection__email" in arch,
            "Fields view get must return architecture with fields created dynamicaly",
        )

        # test the code path where we extract an embedded list for o2m fields
        result = self.MassEditingWizard.with_context(
            server_action_id=self.mass_editing_company.id,
            active_ids=[],
        ).get_view(view_id=view_id.id)
        arch = result.get("arch", "")

        self.assertTrue(
            "<list editable=" in arch
            or "form_view_ref" in arch
            or "list_view_ref" in arch,
            "Fields view get return architecture with embedded list"
            " or with context of list/form view reference",
        )

    def test_wzd_clean_check_company_field_domain(self):
        """
        Test company field domain replacement
        """
        model_name = "res.partner"
        field_domain = [
            ("model", "=", model_name),
            ("name", "=", "company_id"),
        ]
        field = self.env["ir.model.fields"].search(
            field_domain,
        )
        field_info = {
            "name": "company_id",
        }
        result = self.MassEditingWizard._clean_check_company_field_domain(
            self.env[model_name],
            field=field,
            field_info=field_info,
        )
        self.assertDictEqual(
            result,
            field_info,
        )

        model_name = "res.partner"
        field_name = "parent_id"
        field_domain = [
            ("model", "=", model_name),
            ("name", "=", field_name),
        ]
        field = self.env["ir.model.fields"].search(
            field_domain,
        )
        field_info = {
            "name": field_name,
        }
        model = self.env[model_name]
        model._fields[field_name].check_company = True
        result = self.MassEditingWizard._clean_check_company_field_domain(
            model,
            field=field,
            field_info=field_info,
        )
        self.assertEqual(
            result.get("domain"),
            "[]",
        )

    def test_wiz_read_fields(self):
        """Test whether read method returns all fields or not."""
        fields = self.MassEditingWizard.with_context(
            server_action_id=self.mass_editing_user.id,
            active_ids=[],
        ).fields_get()
        fields = list(fields.keys())
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

        fields.remove("selection__email")
        result = mass_wizard.read(fields=fields)[0]
        self.assertTrue(
            "selection__email" not in result,
        )

    def test_mass_edit_country_group(self):
        """Test Case for MASS EDITING which will check if translation
        was loaded for new country group, and if they are removed
        as well as the value for the abbreviation for the country group."""
        self.assertEqual(
            self.country_group.with_context(lang="de_DE").code,
            "GUS",
            "Translation for Country Group's Abbreviation was not loaded properly.",
        )
        # Removing country group code with mass edit action
        vals = {"selection__code": "remove"}
        self._create_wizard_and_apply_values(
            self.mass_editing_country_group, self.country_group, vals
        )
        self.assertEqual(
            self.country_group.code,
            False,
            "Country Group's Abbreviation should be removed.",
        )
        # Checking if translations were also removed
        self.assertEqual(
            self.country_group.with_context(lang="de_DE").code,
            False,
            "Translation for Country Group's Abbreviation was not removed properly.",
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

    def test_mass_edit_o2m_banks(self):
        """Test Case for MASS EDITING which will remove and add
        Partner's bank o2m."""
        # Set another bank (must replace existing one)
        bank_vals = {"acc_number": "account number"}
        self.user.write(
            {
                "bank_ids": [(6, 0, []), (0, 0, bank_vals)],
            }
        )
        vals = {
            "selection__bank_ids": "set_o2m",
            "bank_ids": [(0, 0, dict(bank_vals, acc_number="new number"))],
        }
        self._create_wizard_and_apply_values(self.mass_editing_user, self.user, vals)
        self.assertEqual(self.user.bank_ids.acc_number, "new number")
        # Add bank (must keep existing one)
        vals = {
            "selection__bank_ids": "add_o2m",
            "bank_ids": [(0, 0, dict(bank_vals, acc_number="new number2"))],
        }
        self._create_wizard_and_apply_values(self.mass_editing_user, self.user, vals)
        self.assertEqual(
            self.user.bank_ids.mapped("acc_number"), ["new number", "new number2"]
        )
        # Set empty list (must remove all banks)
        vals = {"selection__bank_ids": "set_o2m"}
        self._create_wizard_and_apply_values(self.mass_editing_user, self.user, vals)
        self.assertFalse(self.user.bank_ids)

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
        dist_categ_id = self.env["res.partner.category"].create({"name": "dist_categ"})
        vend_categ_id = self.env["res.partner.category"].create({"name": "vend_categ"})
        vals = {
            "selection__category_id": "add",
            "category_id": [(4, dist_categ_id.id), (4, vend_categ_id.id)],
        }
        self._create_wizard_and_apply_values(self.mass_editing_user, self.user, vals)
        self.assertTrue(
            all(
                item in self.user.category_id.ids
                for item in [dist_categ_id.id, vend_categ_id.id]
            ),
            "Partner's category should be added.",
        )
        # Remove one m2m category
        vals = {
            "selection__category_id": "remove_m2m",
            "category_id": [[4, vend_categ_id.id]],
        }
        self._create_wizard_and_apply_values(self.mass_editing_user, self.user, vals)
        self.assertTrue(
            [dist_categ_id.id] == self.user.category_id.ids,
            "User's category should be removed.",
        )

    def test_check_field_model_constraint(self):
        """Test that it's not possible to create inconsistent mass edit actions"""
        with self.assertRaises(ValidationError):
            self.mass_editing_user.write(
                {"model_id": self.env.ref("base.model_res_country").id}
            )

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

        mass_edit_line = self.mass_editing_partner.mass_edit_line_ids.filtered(
            lambda line: line.field_id == self.env.ref("base.field_res_partner__email")
        )
        # Test change on mass_edit_line field_id : set widget_option
        mass_edit_line_form = Form(mass_edit_line)
        mass_edit_line_form.field_id = self.env.ref(
            "base.field_res_partner__category_id"
        )
        self.assertEqual(mass_edit_line_form.widget_option, "many2many_tags")
        mass_edit_line_form.field_id = self.env.ref(
            "base.field_res_partner__image_1920"
        )
        self.assertEqual(mass_edit_line_form.widget_option, "image")

        mass_edit_line_form.field_id = self.env.ref(
            "base.field_res_partner__country_id"
        )
        self.assertFalse(mass_edit_line_form.widget_option)

    def test_onchange_call(self):
        """Onchange call does not error on dynamically added fields"""
        self.env["mass.editing.wizard"].with_context(
            active_ids=self.env.user.ids,
            active_model=self.env.user._name,
            server_action_id=self.mass_editing_user.id,
        ).onchange(
            values={},
            field_names={},
            fields_spec={
                "selection__email": {},
                "email": {},
            },
        )

    def test_onchange_model_id(self):
        """Test super call of `_onchange_model_id`"""

        IrActionsServer._onchange_model_id = fake_onchange_model_id
        result = self.ServerAction._onchange_model_id()
        self.assertEqual(
            result,
            fake_onchange_model_id(self),
        )

        del IrActionsServer._onchange_model_id
        result = self.ServerAction._onchange_model_id()
        self.assertEqual(
            result,
            None,
        )
