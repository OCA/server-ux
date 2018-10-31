# Copyright 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# Copyright 2018 Aitor Bouzas <aitor.bouzas@adaptivecity.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import ast

from odoo.tests import common
from odoo.modules import registry
from ..hooks import uninstall_hook


class TestMassEditing(common.SavepointCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super(TestMassEditing, cls).setUpClass()
        # Model connections
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        model_obj = cls.env['ir.model']
        cls.mass_wiz_obj = cls.env['mass.editing.wizard']
        cls.mass_object_model = cls.env['mass.object']
        cls.res_partner_model = cls.env['res.partner']
        cls.ir_translation_model = cls.env['ir.translation']
        cls.lang_model = cls.env['res.lang']
        # Shared data for test methods
        cls.partner = cls._create_partner()
        cls.partner_model = model_obj.\
            search([('model', '=', 'res.partner')])
        cls.user_model = model_obj.search([('model', '=', 'res.users')])
        cls.fields_model = cls.env['ir.model.fields'].\
            search([('model_id', '=', cls.partner_model.id),
                    ('name', 'in', ['email', 'phone', 'category_id', 'comment',
                                    'country_id', 'customer', 'child_ids',
                                    'title', 'company_type'])])
        cls.mass = cls._create_mass_editing(
            cls.partner_model, cls.fields_model, 'Partner')
        cls.copy_mass = cls.mass.copy()
        cls.user = cls._create_user()
        cls.res_partner_title_model = cls.env['res.partner.title']
        cls.partner_title = cls._create_partner_title()
        cls.partner_title_model = model_obj.search(
            [('model', '=', 'res.partner.title')])
        cls.fields_partner_title_model = cls.env['ir.model.fields'].search(
            [('model_id', '=', cls.partner_title_model.id),
             ('name', 'in', ['abbreviation'])])
        cls.mass_partner_title = cls._create_mass_editing(
            cls.partner_title_model, cls.fields_partner_title_model,
            'Partner Title')

    @classmethod
    def _create_partner(cls):
        """Create a Partner."""
        categ_ids = cls.env['res.partner.category'].search([]).ids
        return cls.res_partner_model.create({
            'name': 'Test Partner',
            'email': 'example@yourcompany.com',
            'phone': 123456,
            'category_id': [(6, 0, categ_ids)],
            'notify_email': 'always'
        })

    @classmethod
    def _create_partner_title(cls):
        """Create a Partner Title."""
        # Loads German to work with translations
        cls.lang_model.load_lang('de_DE')
        # Creating the title in English
        partner_title = cls.res_partner_title_model.create({
            'name': 'Ambassador',
            'shortcut': 'Amb.',
        })
        # Adding translated terms
        ctx = {'lang': 'de_DE'}
        partner_title.with_context(ctx).write({
            'name': 'Botschafter',
            'shortcut': 'Bots.'})
        return partner_title

    @classmethod
    def _create_user(cls):
        return cls.env['res.users'].create({
            'name': 'Test User',
            'login': 'test_login',
            'email': 'test@test.com',
        })

    @classmethod
    def _create_mass_editing(cls, model, fields, model_name):
        """Create a Mass Editing with Partner as model and
        email field of partner."""
        mass = cls.mass_object_model.create({
            'name': 'Mass Editing for {0}'.format(model_name),
            'model_id': model.id,
            'field_ids': [(6, 0, fields.ids)]
        })
        mass.create_action()
        return mass

    def _apply_action(self, obj, vals):
        """Create Wizard object to perform mass editing to
        REMOVE field's value."""
        ctx = {
            'active_id': obj.id,
            'active_ids': obj.ids,
            'active_model': obj._name,
        }
        return self.mass_wiz_obj.with_context(ctx).create(vals)

    def test_wiz_fields_view_get(self):
        """Test whether fields_view_get method returns arch or not."""
        ctx = {
            'mass_editing_object': self.mass.id,
            'active_id': self.partner.id,
            'active_ids': self.partner.ids,
            'active_model': 'res.partner',
        }
        result = self.mass_wiz_obj.with_context(ctx).fields_view_get()
        self.assertTrue(result.get('arch'),
                        'Fields view get must return architecture.')

    def test_onchange_model(self):
        """Test whether onchange model_id returns model_id in list"""
        new_mass = self.mass_object_model.new({'model_id': self.user_model.id})
        new_mass._onchange_model_id()
        model_list = ast.literal_eval(new_mass.model_list)
        self.assertTrue(self.user_model.id in model_list,
                        'Onchange model list must contains model_id.')

    def test_wiz_read_fields(self):
        """Test whether read method returns all fields or not."""
        ctx = {
            'mass_editing_object': self.mass.id,
            'active_id': self.partner.id,
            'active_ids': self.partner.ids,
            'active_model': 'res.partner',
        }
        fields_view = self.mass_wiz_obj.with_context(ctx).fields_view_get()
        fields = list(fields_view['fields'].keys())
        # add a real field
        fields.append('display_name')
        vals = {
            'selection__email': 'remove',
            'selection__phone': 'remove',
        }
        mass_wiz_obj = self._apply_action(self.partner, vals)
        result = mass_wiz_obj.read(fields)[0]
        self.assertTrue(all([field in result for field in fields]),
                        'Read must return all fields.')

    def test_mass_edit_partner_title(self):
        """Test Case for MASS EDITING which will check if translation
        was loaded for new partner title, and if they are removed
        as well as the value for the abbreviation for the partner title."""
        search_domain = [('res_id', '=', self.partner_title.id),
                         ('type', '=', 'model'),
                         ('name', '=', 'res.partner.title,shortcut'),
                         ('lang', '=', 'de_DE')]
        translation_ids = self.ir_translation_model.search(search_domain)
        self.assertEqual(len(translation_ids), 1,
                         'Translation for Partner Title\'s Abbreviation '
                         'was not loaded properly.')
        # Removing partner title with mass edit action
        vals = {
            'selection__shortcut': 'remove',
        }
        self._apply_action(self.partner_title, vals)
        self.assertEqual(self.partner_title.shortcut, False,
                         'Partner Title\'s Abbreviation should be removed.')
        # Checking if translations were also removed
        translation_ids = self.ir_translation_model.search(search_domain)
        self.assertEqual(len(translation_ids), 0,
                         'Translation for Partner Title\'s Abbreviation '
                         'was not removed properly.')

    def test_mass_edit_email(self):
        """Test Case for MASS EDITING which will remove and after add
        Partner's email and will assert the same."""
        # Remove email address
        vals = {
            'selection__email': 'remove',
            'selection__phone': 'remove',
        }
        self._apply_action(self.partner, vals)
        self.assertEqual(self.partner.email, False,
                         'Partner\'s Email should be removed.')
        # Set email address
        vals = {
            'selection__email': 'set',
            'email': 'sample@mycompany.com',
        }
        self._apply_action(self.partner, vals)
        self.assertNotEqual(self.partner.email, False,
                            'Partner\'s Email should be set.')

    def test_mass_edit_m2m_categ(self):
        """Test Case for MASS EDITING which will remove and add
        Partner's category m2m."""
        # Remove m2m categories
        vals = {
            'selection__category_id': 'remove_m2m',
        }
        self._apply_action(self.partner, vals)
        self.assertNotEqual(self.partner.category_id, False,
                            'Partner\'s category should be removed.')
        # Add m2m categories
        dist_categ_id = self.env.ref('base.res_partner_category_14').id
        vend_categ_id = self.env.ref('base.res_partner_category_0').id
        vals = {
            'selection__category_id': 'add',
            'category_id': [[6, 0, [dist_categ_id, vend_categ_id]]],
        }
        wiz_action = self._apply_action(self.partner, vals)
        self.assertTrue(all(item in self.partner.category_id.ids
                            for item in [dist_categ_id, vend_categ_id]),
                        'Partner\'s category should be added.')
        # Remove one m2m category
        vals = {
            'selection__category_id': 'remove_m2m',
            'category_id': [[6, 0, [vend_categ_id]]],
        }
        wiz_action = self._apply_action(self.partner, vals)
        self.assertTrue([dist_categ_id] == self.partner.category_id.ids,
                        'Partner\'s category should be removed.')
        # Check window close action
        res = wiz_action.action_apply()
        self.assertTrue(res['type'] == 'ir.actions.act_window_close',
                        'IR Action must be window close.')

    def test_mass_edit_copy(self):
        """Test if fields one2many field gets blank when mass editing record
        is copied.
        """
        self.assertEqual(self.copy_mass.field_ids.ids, [],
                         'Fields must be blank.')

    def test_sidebar_action(self):
        """Test if Sidebar Action is added / removed to / from give object."""
        action = self.mass.ref_ir_act_window_id\
            and self.mass.ref_ir_act_window_id.binding_model_id
        self.assertTrue(action, 'Sidebar action must be exists.')
        # Remove the sidebar actions
        self.mass.unlink_action()
        action = self.mass.ref_ir_act_window_id
        self.assertFalse(action, 'Sidebar action must be removed.')

    def test_special_search(self):
        """Test for the special search."""
        fields = self.env['ir.model.fields'].search(
            [('ttype', 'not in', ['reference', 'function']),
             ('mass_editing_domain', 'in', '[1,2]')]
        )
        self.assertTrue(len(fields),
                        "Special domain 'mass_editing_domain'"
                        " should find fields in different models.")

    def test_unlink_mass(self):
        """Test if related actions are removed when mass editing
        record is unlinked."""
        mass_action_id = self.mass.ref_ir_act_window_id.id
        mass_object_id = self.mass.id
        mass_id = self.env['mass.object'].browse(mass_object_id)
        mass_id.unlink()
        value_cnt = self.env['ir.actions.act_window'].search([
            ('id', '=', mass_action_id)], count=True)
        self.assertTrue(value_cnt == 0,
                        "Sidebar action must be removed when mass"
                        " editing is unlinked.")

    def test_uninstall_hook(self):
        """Test if related actions are removed when mass editing
        record is uninstalled."""
        uninstall_hook(self.cr, registry)
        mass_action_id = self.mass.ref_ir_act_window_id.id
        value_cnt = len(self.env['ir.actions.act_window'].browse(
                        mass_action_id))
        self.assertTrue(value_cnt == 0,
                        "Sidebar action must be removed when mass"
                        " editing module is uninstalled.")
