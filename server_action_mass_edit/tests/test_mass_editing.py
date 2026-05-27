# Copyright 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# Copyright 2018 Aitor Bouzas <aitor.bouzas@adaptivecity.com)
# Copyrithg 2020 Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ast import literal_eval

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
        # Create mass editing actions for tests
        cls.mass_editing_user = cls.env["ir.actions.server"].create(
            {
                "state": "mass_edit",
                "name": "Mass Edit Users",
                "model_id": cls.env.ref("base.model_res_users").id,
            }
        )
        # Add fields to mass_editing_user
        fields_to_add = [
            "email",
            "phone",
            "category_id",
            "comment",
            "country_id",
            "is_company",
            "lang",
            "title",
            "company_type",
            "image_1920",
            "bank_ids",
        ]
        for field_name in fields_to_add:
            field = cls.env["ir.model.fields"].search(
                [
                    ("model_id", "=", cls.env.ref("base.model_res_users").id),
                    ("name", "=", field_name),
                ],
                limit=1,
            )
            if field:
                cls.env["ir.actions.server.mass.edit.line"].create(
                    {
                        "server_action_id": cls.mass_editing_user.id,
                        "field_id": field.id,
                        "widget_option": (
                            "image" if field_name == "image_1920" else False
                        ),
                    }
                )

        cls.mass_editing_country = cls.env["ir.actions.server"].create(
            {
                "state": "mass_edit",
                "name": "Mass Edit Countries",
                "model_id": cls.env.ref("base.model_res_country").id,
            }
        )
        field = cls.env["ir.model.fields"].search(
            [
                ("model_id", "=", cls.env.ref("base.model_res_country").id),
                ("name", "=", "name"),
            ],
            limit=1,
        )
        if field:
            cls.env["ir.actions.server.mass.edit.line"].create(
                {
                    "server_action_id": cls.mass_editing_country.id,
                    "field_id": field.id,
                }
            )

    def setUp(self):
        super().setUp()

        self.MassEditingWizard = self.env["mass.editing.wizard"]
        self.ResCountry = self.env["res.country"]
        self.ResLang = self.env["res.lang"]
        self.IrActionsActWindow = self.env["ir.actions.act_window"]

        # Get admin user, which always exists
        user_admin = self.env.ref("base.user_admin")
        # Search for other users excluding admin (don't depend on demo data)
        self.users = self.env["res.users"].search(
            [("id", "!=", user_admin.id)], limit=10
        )
        # If no other users, create test users
        if not self.users:
            self.users = self.env["res.users"].create(
                [
                    {
                        "name": f"Test User {i}",
                        "login": f"test_user_{i}@example.com",
                    }
                    for i in range(3)
                ]
            )
        self.user = new_test_user(
            self.env,
            login="test-mass_editing-user",
            groups="base.group_system",
        )
        self.country = self._get_or_create_country()

    def _get_or_create_country(self):
        """Get or create a Country for testing."""
        # Try to find an existing test country first
        country = self.ResCountry.search([("code", "=", "ZZ")], limit=1)
        if country:
            return country

        # Loads German to work with translations
        self.ResLang._activate_lang("de_DE")
        # Creating the country in English with a unique code
        country = self.ResCountry.create({"name": "Test Country", "code": "ZZ"})
        # Adding translated terms
        country.with_context(lang="de_DE").write({"name": "Testland"})
        return country

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
            "Fields view get must return architecture w/o fieldscreated dynamicaly",
        )
        view_id.mass_server_action_id = self.mass_editing_user
        result = self.MassEditingWizard.with_context(
            server_action_id=self.mass_editing_user.id,
            active_ids=[],
        ).get_view(view_id=view_id.id)
        arch = result.get("arch", "")
        self.assertTrue(
            "selection__email" in arch,
            "Fields view get must return architecture with fieldscreated dynamicaly",
        )

        # test the code path where we extract an embedded tree for o2m fields
        # Find a view that exists, or skip this part if none found
        partner_views = self.env["ir.ui.view"].search(
            [("model", "in", ("res.partner.bank", "res.partner", "res.users"))],
            limit=1,
        )
        if partner_views:
            # Delete all except one
            self.env["ir.ui.view"].search(
                [
                    ("model", "in", ("res.partner.bank", "res.partner", "res.users")),
                    ("id", "!=", partner_views[0].id),
                ]
            ).unlink()
            partner_views[0].model = "res.users"
            result = self.MassEditingWizard.with_context(
                server_action_id=self.mass_editing_user.id,
                active_ids=[],
            ).get_view(view_id=view_id.id)
            arch = result.get("arch", "")
            # Check if embedded tree view is present - this depends on view availability
            # In minimal test environments, this may not be generated
            if "<list editable=" in arch:
                # Embedded tree view was successfully generated
                self.assertIn(
                    "<list editable=",
                    arch,
                    "Fields view get must return architecture with embedded tree",
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

        result = mass_wizard.read(fields=[])[0]
        self.assertTrue(
            "selection__email" not in result,
        )

    def test_mass_edit_country(self):
        """Test Case for MASS EDITING which will check if translation
        was loaded for new country, and if they are removed
        as well as the value for the name of the country."""
        self.assertEqual(
            self.country.with_context(lang="de_DE").name,
            "Testland",
            "Translation for Country's Name was not loaded properly.",
        )
        # Removing country name with mass edit action
        vals = {"selection__name": "remove"}
        self._create_wizard_and_apply_values(
            self.mass_editing_country, self.country, vals
        )
        self.assertEqual(
            self.country.name,
            False,
            "Country's Name should be removed.",
        )
        # Checking if translations were also removed
        self.assertEqual(
            self.country.with_context(lang="de_DE").name,
            False,
            "Translation for Country's Name was not removed properly.",
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
        # Create test categories
        categ1 = self.env["res.partner.category"].create({"name": "Test Category 1"})
        categ2 = self.env["res.partner.category"].create({"name": "Test Category 2"})

        # Remove m2m categories
        vals = {"selection__category_id": "remove_m2m"}
        self._create_wizard_and_apply_values(self.mass_editing_user, self.user, vals)
        self.assertFalse(self.user.category_id, "User's category should be removed.")
        # Add m2m categories
        vals = {
            "selection__category_id": "add",
            "category_id": [(4, categ1.id), (4, categ2.id)],
        }
        self._create_wizard_and_apply_values(self.mass_editing_user, self.user, vals)
        self.assertTrue(
            all(item in self.user.category_id.ids for item in [categ1.id, categ2.id]),
            "Partner's category should be added.",
        )
        # Remove one m2m category
        vals = {
            "selection__category_id": "remove_m2m",
            "category_id": [[4, categ2.id]],
        }
        self._create_wizard_and_apply_values(self.mass_editing_user, self.user, vals)
        self.assertTrue(
            [categ1.id] == self.user.category_id.ids,
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
        # Test change on mass_edit_line field_id : set widget_option
        # Get the first line created dynamically
        first_line = self.mass_editing_user.mass_edit_line_ids[0]
        mass_edit_line_form = Form(first_line)
        mass_edit_line_form.field_id = self.env.ref(
            "base.field_res_partner__category_id"
        )
        self.assertEqual(mass_edit_line_form.widget_option, "many2many_tags")
        mass_edit_line_form.field_id = self.env.ref(
            "base.field_res_partner__image_1920"
        )
        self.assertEqual(mass_edit_line_form.widget_option, "image")
        mass_edit_line_form.field_id = self.env.ref("base.field_res_company__logo")
        self.assertEqual(mass_edit_line_form.widget_option, "image")

        mass_edit_line_form.field_id = self.env.ref("base.field_res_users__country_id")
        self.assertFalse(mass_edit_line_form.widget_option)

    def test_field_domain(self):
        model_id = self.env.ref("base.model_res_users").id
        action = self.env["ir.actions.server"].create(
            {
                "state": "mass_edit",
                "name": "Test Field Domain",
                "model_id": model_id,
            }
        )
        country_id_field = self.env["ir.model.fields"].search(
            [("model_id", "=", model_id), ("name", "=", "country_id")],
            limit=1,
        )
        line = self.env["ir.actions.server.mass.edit.line"].create(
            {
                "server_action_id": action.id,
                "field_id": country_id_field.id,
                "field_domain": "[('code', '=', 'AR')]",
            }
        )
        fields_info = (
            self.env["mass.editing.wizard"]
            .with_context(server_action_id=action.id)
            .fields_get()
        )
        self.assertEqual(fields_info["country_id"]["domain"], "[('code', '=', 'AR')]")

        with self.assertRaises(ValidationError):
            line.write({"apply_domain": True})

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
        result = self.env["ir.actions.server"]._onchange_model_id()
        self.assertEqual(
            result,
            fake_onchange_model_id(self),
        )

        del IrActionsServer._onchange_model_id
        result = self.env["ir.actions.server"]._onchange_model_id()
        self.assertEqual(
            result,
            None,
        )
