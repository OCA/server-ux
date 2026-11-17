# Copyright 2026 Camptocamp SA
# @author Akim Juillerat <akim.juillerat@camptocamp.com>
# @author Ricardo Almeida Soares <ricardo.almeidasoares@camptocamp.com>
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models


class LineNumberingMixin(models.AbstractModel):
    """Number the lines of a record with stable positions.

    The lines are renumbered in their order whenever they are added or
    removed. Inheriting models must set:

    - `_line_numbering_lines_field`: the one2many holding the lines;
    - `_line_numbering_position_field`: the field of the lines storing their
      position, an integer (or a char) field to add on the lines' model.

    And can set or override:

    - `_line_numbering_step`: the gap between two positions (default 1);
    - `_line_renumber_needed()`: whether a record is renumbered
      automatically (e.g. not once sent to a partner);
    - `_line_renumber_trigger_fields()`: the `write()` keys that trigger
      the renumbering, when `_line_numbering_lines_field` is a computed
      one2many;
    - `_line_renumber_get_lines()`: which lines are numbered, and in which
      order.
    """

    _name = "line.numbering.mixin"
    _description = "Provides numbering of lines"

    # One2many field holding the lines to number
    _line_numbering_lines_field = None
    # Integer (or char) field of the lines storing their position
    _line_numbering_position_field = None
    # Gap between two consecutive positions
    _line_numbering_step = 1

    def renumber_lines_positions(self):
        """Give the lines of `self` consecutive positions, in their order.

        Positions are multiples of `_line_numbering_step`. Only the lines whose
        position changes are written.
        """
        position_field = self._line_numbering_position_field
        for index, line in enumerate(self._line_renumber_get_lines(), start=1):
            position = self._line_numbering_value(line, index)
            if line[position_field] != position:
                line.write({position_field: position})

    def _line_numbering_value(self, line, index):
        """Position of `line`, the `index`-th line (1-based) to number.

        Returned as a string when the position field is a char field, so that
        unchanged positions compare equal and are not written again.
        """
        position = index * self._line_numbering_step
        if line._fields[self._line_numbering_position_field].type == "char":
            return str(position)
        return position

    def _line_renumber_get_lines(self):
        """Lines of `self`, in the order they get their positions."""
        return self[self._line_numbering_lines_field].sorted()

    def _line_renumber_trigger_fields(self):
        """Vals keys on `write()` that should re-trigger auto-renumbering.

        Defaults to `_line_numbering_lines_field`; override when the field
        iterated by `renumber_lines_positions()` is a computed one2many (e.g.
        filtered on another stored field), since a computed field never
        appears as a key in `write()` vals.
        """
        return [self._line_numbering_lines_field]

    def _line_renumber_needed(self):
        """Whether the automatic create/write hook may renumber `self`.

        Override per model to opt out for a specific condition (e.g. a
        record already sent to a third party). Defaults to skipping only
        when the `skip_line_auto_renumber` context key is set.
        """
        self.ensure_one()
        return not self.env.context.get("skip_line_auto_renumber")

    def _auto_renumber_lines_positions(self):
        """Renumber the records of `self` that allow automatic renumbering."""
        for record in self:
            if record._line_renumber_needed():
                record.renumber_lines_positions()

    @api.model_create_multi
    def create(self, vals_list):
        """Number the lines of the new records."""
        records = super().create(vals_list)
        records._auto_renumber_lines_positions()
        return records

    def write(self, vals):
        """Renumber the lines when the lines field is written."""
        res = super().write(vals)
        if any(field in vals for field in self._line_renumber_trigger_fields()):
            self._auto_renumber_lines_positions()
        return res
