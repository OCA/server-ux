# Issues

- The module is implemented by patching the method `name_create`. When used, it may break odoo standard code.
- There is a known issue when we activate the option on `res.partner` and using the module helpdesk.

If you do so, you will break the feature of creating an `helpdesk.ticket` when receiving an email.
When we receive an email. If the contact doesn't exist, odoo will use the method `name_create`.
This module will raise a UserError and prevent the creation of both: `helpdesk.ticket` and `res.partner`.
