To configure this module, you need to:

#. Go to *Setting > Fiend Swaps > Fiend Swaps*.
#. Create a new object and set the following data as an example:

   #. Set name 'Change Language'.
   #. Select 'Contact' as a Model.
   #. Select 'Language (res.partner)' as 'Field'.
   #. Add a new 'Sub-field chain' with this value 'child_ids.lang'.
   #. Add a new Constraint with this 'Expression':
      ```bool(records.mapped('parent_id')```

#. Click on 'Add action' smart button to add a new menu action in
   'res.partner' tree view named 'Change Language'.
