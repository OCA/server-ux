Restrict access to a **Window Action**.

Window actions normally have a wizard - window that opens after you run action.

Window actions have as Destination Model a model of the wizard. Not a target model.

Lets say you want to limit access to the window action Create Invoices for Sale Order.

#. Enable debug mode.
#. Select multiple records in the Sale Orders list view.
#. Action -> Create Invoices.
#. Click bug symbol. Click Edit Action.
#. Go to Security tab.
#. Create restrictions lines and save.

Restrict access to a **Server Action**.

Server actions dont have a wizard. They are linked directly to a target model. They are performed right away after you click action.

Lets say you want to limit access to the server action Mark Quotation as Sent for Sale Order.

#. Enable debug mode.
#. Go to Settings -> Technical -> Server Actions.
#. Search for  Mark Quotation as Sent. You can see in the Model field it is Sale Order.
#. Go to Security tab.
#. Create restrictions lines and save.
