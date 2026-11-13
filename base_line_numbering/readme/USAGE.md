This module is meant for developers. Inherit the mixin on the parent model and
declare which lines to number and where to store their position:

``` python
class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = ["purchase.order", "line.numbering.mixin"]

    _line_field = "order_line"
    _line_position_field = "position"
```

- `_line_field`: the one2many field holding the lines to number.
- `_line_position_field`: the char field of the lines that stores the
  position.

`renumber_lines_positions()` numbers the lines of the records explicitly.
`create()` and `write()` call it automatically when the lines change.

The behaviour can be adapted by overriding:

- `_can_auto_renumber_lines()`: return `False` to skip the automatic
  renumbering for a record (e.g. a locked one). By default, it is skipped
  only when the `skip_line_auto_renumber` context key is set.
- `_line_trigger_fields()`: the `write()` keys that re-trigger the
  numbering. Defaults to `[_line_field]`. Override it when `_line_field` is
  a computed one2many, which never appears in `write()` values.
- `_get_lines_to_renumber()`: the lines to number, in the order they get
  their positions. Defaults to the lines of `_line_field` in their model's
  order.
