# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common
from odoo.modules import registry
from ..hooks import uninstall_hook


class TestChainedSwapper(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestChainedSwapper, cls).setUpClass()
        cls.env['res.lang'].load_lang('es_ES')
        res_partner = cls.env['res.partner']
        cls.partner_parent = res_partner.create(
            {'name': 'parent partner cs', 'lang': 'en_US'})
        cls.partner_child_1 = res_partner.create(
            {'name': 'partner child1 cs', 'parent_id': cls.partner_parent.id})
        cls.partner_child_2 = res_partner.create(
            {'name': 'partner child2 cs', 'parent_id': cls.partner_parent.id})
        cls.chained_swapper = cls.env.ref(
            "chained_swapper.chained_swapper_demo")

    def test_create_unlink_action(self):
        """Test if Sidebar Action is added / removed to / from give object."""
        action = self.chained_swapper.ref_ir_act_window_id\
            and self.chained_swapper.ref_ir_act_window_id.binding_model_id
        self.assertTrue(action)
        # Remove the action
        self.chained_swapper.unlink_action()
        action = self.chained_swapper.ref_ir_act_window_id
        self.assertFalse(action)
        # Add an action
        self.chained_swapper.add_action()
        action = self.chained_swapper.ref_ir_act_window_id \
            and self.chained_swapper.ref_ir_act_window_id.binding_model_id
        self.assertTrue(action)

    def test_unlink_chained_swapper(self):
        """Test if related actions are removed when a chained swapper
        record is unlinked."""
        action_id = self.chained_swapper.ref_ir_act_window_id.id
        self.chained_swapper.unlink()
        action = self.env['ir.actions.act_window'].search([
            ('id', '=', action_id)])
        self.assertFalse(action)

    def test_change_constrained_partner_language(self):
        self.env['chained.swapper.wizard'].with_context(
            active_model='res.partner',
            active_id=self.partner_parent.id,
            active_ids=(self.partner_parent | self.partner_child_1).ids,
            chained_swapper_id=self.chained_swapper.id
        ).create({'lang': 'es_ES'})

    def test_change_partner_language(self):
        all_partner = (
            self.partner_parent | self.partner_child_1 | self.partner_child_2)
        self.assertEqual(all_partner.mapped('lang'), ['en_US']*3)
        self.env['chained.swapper.wizard'].with_context(
            active_model='res.partner',
            active_id=self.partner_parent.id,
            active_ids=[self.partner_parent.id],
            chained_swapper_id=self.chained_swapper.id
        ).create({'lang': 'es_ES'})
        self.assertEqual(all_partner.mapped('lang'), ['es_ES']*3)

    def _test_uninstall_hook(self):
        """Test if related actions are removed when mass editing
        record is uninstalled."""
        action_id = self.chained_swapper.ref_ir_act_window_id.id
        uninstall_hook(self.cr, registry)
        self.assertFalse(self.env['ir.actions.act_window'].browse(action_id))
