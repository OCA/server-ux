# Copyright 2026 Camptocamp SA
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.fields import Command
from odoo.orm.model_classes import add_to_registry
from odoo.tests import TransactionCase


class TestLineNumbering(TransactionCase):
    @classmethod
    def setUpClass(cls):
        """Load the fake order and line models."""
        super().setUpClass()
        from .fake_models import LineNumberingTestLine, LineNumberingTestOrder

        fake_models = (LineNumberingTestOrder, LineNumberingTestLine)
        model_names = [model._name for model in fake_models]
        for model in fake_models:
            add_to_registry(cls.registry, model)
        cls.registry._setup_models__(cls.env.cr, model_names)
        cls.registry.init_models(cls.env.cr, model_names, {"models_to_check": True})
        for model_name in model_names:
            cls.addClassCleanup(cls.registry.__delitem__, model_name)
        cls.order_model = cls.env["line.numbering.test.order"]

    def _create_order(self, *names, **kw):
        """Create an order with one line per name."""
        return self.order_model.create(
            {
                "name": "Test",
                "line_ids": [Command.create({"name": name}) for name in names],
                **kw,
            }
        )

    def _positions(self, order):
        """Positions of the order's lines, in their order."""
        return order.line_ids.mapped("position")

    def test_create_numbers_lines(self):
        """Lines get positions 10, 20, 30 when the order is created."""
        order = self._create_order("A", "B", "C")
        self.assertEqual(self._positions(order), ["10", "20", "30"])

    def test_write_add_line_renumbers(self):
        """A line added through the lines field is numbered after the others."""
        order = self._create_order("A")
        order.write({"line_ids": [Command.create({"name": "B"})]})
        self.assertEqual(self._positions(order), ["10", "20"])

    def test_write_remove_line_renumbers(self):
        """Removing a line closes the gap in the positions."""
        order = self._create_order("A", "B", "C")
        order.write({"line_ids": [Command.delete(order.line_ids[0].id)]})
        self.assertEqual(self._positions(order), ["10", "20"])

    def test_positions_follow_line_order(self):
        """Positions follow the lines' model order, not their creation order."""
        order = self._create_order("A", "B")
        line_a, line_b = order.line_ids
        line_b.sequence = 1
        order.renumber_lines_positions()
        self.assertEqual(line_b.position, "10")
        self.assertEqual(line_a.position, "20")

    def test_write_other_field_does_not_renumber(self):
        """Writing a field other than the lines leaves positions untouched."""
        order = self._create_order("A", "B")
        order.line_ids[0].position = "99"
        order.write({"name": "Renamed"})
        self.assertEqual(self._positions(order), ["99", "20"])

    def test_skip_context_key(self):
        """The skip context key disables only the automatic numbering."""
        order = self._create_order("A", "B").with_context(skip_line_auto_renumber=True)
        order.write({"line_ids": [Command.create({"name": "C"})]})
        self.assertEqual(self._positions(order), ["10", "20", False])
        order.renumber_lines_positions()
        self.assertEqual(self._positions(order), ["10", "20", "30"])
