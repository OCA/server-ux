A wizard interface to execute Odoo server actions allowing for user input parameters.

Server Actions can be by end users to manually run automation scripts,
but the only parameter available is the records select to run the action.

This feature allows to present a dialog to the users,
where they can enter parameters to be passed to the server action.

These parameters are made available to be used
in the server action Python code through the environment context.

A usage example could be to copy a Customer Invoice for a period of months.

Key features:

- Select a target model and a corresponding available server action.
- Enter parameters to be passed to the server action via \`context\`:
  - Start Date
  - End Date
  - Text 1
  - Text 2

Server action Python code can then access these via:

``` python
date_start = env.context.get('param_date_start')
date_end = env.context.get('param_date_end')
text_1 = env.context.get('param_1')
text_2 = env.context.get('param_2')
```
