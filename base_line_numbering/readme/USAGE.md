This module is meant for developers. Inherit the mixin on the parent model and
declare which lines to number and where to store their position:

``` python
class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = ["purchase.order", "line.numbering.mixin"]

    _line_numbering_lines_field = "order_line"
    _line_numbering_position_field = "position"
    _line_numbering_step = 10
```

- `_line_numbering_lines_field`: the one2many field holding the lines to
  number.
- `_line_numbering_position_field`: the field of the lines that stores the
  position. It is meant to be an integer field; a char field gets the
  positions as strings (e.g. when it also stores references coming from a
  partner).
- `_line_numbering_step`: the gap between two consecutive positions
  (default: 1).

`renumber_lines_positions()` numbers the lines of the records explicitly.
`create()` and `write()` call it automatically when the lines change.

The behaviour can be adapted by overriding:

- `_line_renumber_needed()`: return `False` to skip the automatic
  renumbering for a record (e.g. a locked one). By default, it is skipped
  only when the `skip_line_auto_renumber` context key is set.
- `_line_renumber_trigger_fields()`: the `write()` keys that re-trigger the
  numbering. Defaults to `[_line_numbering_lines_field]`. Override it when
  `_line_numbering_lines_field` is a computed one2many, which never appears in `write()` values.
- `_line_renumber_get_lines()`: the lines to number, in the order they get
  their positions. Defaults to the lines of `_line_numbering_lines_field` in their model's
  order.
