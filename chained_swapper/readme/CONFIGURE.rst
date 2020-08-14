To configure this module, you need to:

#. Go to *Setting > Field Swaps > Field Swaps*.
#. Create a new object and set the following data as an example:

   * Name for identifying it and use it for the action name.
   * Select the source model where the swap will be started.
   * Select the starting field for which the swap will be done.
   * Add several chained fields. They are expressed as a string using
     dot notation, taking the source model as beginning for looking there
     the first field, and continuing from there drilling through. Example:
     `picking_ids.partner_id` for `sale.order` model will go to the linked
     deliveries orders, and change the customer there.
   * Add possible constraints for restricting the chained swap. They are
     Python expressions that must be one line that is evaluated as boolean.
     If the evaluation is true, then a message will be thrown and no swap
     will be allowed. You can use the variable `records` in your code, that
     will be referring the selected records for doing the swap. Example: for
     restricting sales orders that have a delivery order validated:

     `any(p.state == 'done' for p in records.mapped('picking_ids.state'))`

     Each constraint has a name for identifying it, but also for showing that
     name when displaying the error trying to do the swap.

#. Click on 'Add action' smart button to add a new action in the source model.

On demo databases, you can check the example "Language", that changes the
language of a contact, and propagate it to children contacts.
