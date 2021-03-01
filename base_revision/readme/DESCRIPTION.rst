Making revision(s) of a document is a common need across many area.

This module does not provide a functionality by itself but an abstract model
to implement revision capality in other models
(e.g. purchase orders, sales orders, budgets, expenses...).

**Note:** To be able to use this module in a new model you will need some
development.

See `sale_order_revision <https://github.com/OCA/sale-workflow>`_ as an example of implementation.

Example with sale_order_revision installed,

On a cancelled orders, you can click on the "New copy of Quotation" button. This
will create a new revision of the quotation, with the same base number and a
'-revno' suffix appended. A message is added in the chatter saying that a new
revision was created.

In the form view, a new tab is added that lists the previous revisions, with
the date they were made obsolete and the user who performed the action.

The old revisions of a sale order are flagged as inactive, so they don't
clutter up searches.

**Special Remarks:** Starting on version 14, this module was splitted from sale_order_revision to,

- base_revision
- sale_order_revision
