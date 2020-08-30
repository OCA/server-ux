This module provide abstract models to manage customizable
substates to be applied on different models (sale order, purchase, ...).

example:
--------

* for the quotation state of a sale order we can define 3 substates "In negotiation",
  "Won" and "Lost".
* We can also send mail when the susbstate is reached.

It is not useful for itself. You can see an example of implementation
in the 'purchase_substate' module. (purchase-workflow repository).
