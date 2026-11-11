# Copyright 2026 Camptocamp SA
# @author Akim Juillerat <akim.juillerat@camptocamp.com>
# @author Ricardo Almeida Soares <ricardo.almeidasoares@camptocamp.com>
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models


class LineNumberingMixin(models.AbstractModel):
    _name = "line.numbering.mixin"
    _description = "Provides numbering of lines"

    _line_field = None
    _line_position_field = None

    def renumber_lines_positions(self):
        """Give the lines of `self` the positions 10, 20, 30, ... in their order.

        Only the lines whose position changes are written.
        """
        for cnt, line in enumerate(self._get_lines_to_renumber(), start=1):
            position = str(10 * cnt)
            if line[self._line_position_field] != position:
                line.write({self._line_position_field: position})

    def _get_lines_to_renumber(self):
        """Lines of `self`, in the order they get their positions."""
        return self[self._line_field].sorted()

    def _line_trigger_fields(self):
        """Vals keys on `write()` that should re-trigger auto-renumbering.

        Defaults to `_line_field`; override when the field iterated by
        `renumber_lines_positions()` is a computed one2many (e.g. filtered
        on another stored field), since a computed field never appears as a
        key in `write()` vals.
        """
        return [self._line_field]

    def _can_auto_renumber_lines(self):
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
            if record._can_auto_renumber_lines():
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
        if any(field in vals for field in self._line_trigger_fields()):
            self._auto_renumber_lines_positions()
        return res
