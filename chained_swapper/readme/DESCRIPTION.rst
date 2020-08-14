This module allows to swap the value of a field and propagate it in a chained
way to linked records. Example: changing the delivery address in a confirmed
sales order, it should be changed in its delivery orders as well.

It also allows to apply constraints for not allowing to do that change
according rules, so the business logic is not broken. Example: Don't allow
to change the delivery address if the delivery order is validated.

This module requires some technical knowledge for setting the chained swap and
the constraint, as it's defined through technical names and Python code.

**WARNING**: Use this module with care, as it can screw up database consistency
if swaps are not properly designed .
