On the view xml file, add the context options, i.e.,


* `default_line` is the one2many field
* `default_fields` if defined will default only defined fields, otherwise, all default all fields.

From the above implementation, when a new record is being added from the UI form view,
the context data (one2many default_line and default_fields) is passed in, and default_get() values
from previous line.
